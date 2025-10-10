import pytest
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from extended_sklearn_metrics import (
    calculate_roc_metrics,
    calculate_multiclass_roc_metrics,
    calculate_precision_recall_metrics,
    find_optimal_thresholds,
    create_threshold_analysis_report,
    print_roc_auc_summary
)


class TestROCAUCAnalysis:
    """Test suite for ROC/AUC analysis functionality"""
    
    @pytest.fixture
    def binary_classification_data(self):
        """Create binary classification test data"""
        X, y = make_classification(
            n_samples=200,
            n_features=5,
            n_informative=3,
            n_redundant=1,
            n_clusters_per_class=1,
            weights=[0.6, 0.4],
            random_state=42
        )
        return {
            'X': pd.DataFrame(X, columns=[f'feature_{i}' for i in range(5)]),
            'y': pd.Series(y),
            'model': LogisticRegression(random_state=42)
        }
    
    @pytest.fixture
    def multiclass_classification_data(self):
        """Create multiclass classification test data"""
        X, y = make_classification(
            n_samples=300,
            n_features=4,
            n_informative=3,
            n_redundant=1,
            n_classes=3,
            n_clusters_per_class=1,
            random_state=123
        )
        return {
            'X': pd.DataFrame(X, columns=[f'feature_{i}' for i in range(4)]),
            'y': pd.Series(y),
            'model': RandomForestClassifier(n_estimators=10, random_state=123)
        }
    
    def test_calculate_roc_metrics_basic(self, binary_classification_data):
        """Test basic ROC metrics calculation"""
        roc_metrics = calculate_roc_metrics(
            model=binary_classification_data['model'],
            X=binary_classification_data['X'],
            y=binary_classification_data['y'],
            cv=3
        )
        
        # Check that all required components are present
        required_keys = [
            'fpr', 'tpr', 'thresholds', 'roc_auc',
            'optimal_threshold', 'optimal_tpr', 'optimal_fpr',
            'optimal_youden_index', 'threshold_metrics',
            'y_scores', 'y_true', 'pos_label', 'n_samples'
        ]
        
        for key in required_keys:
            assert key in roc_metrics
        
        # Check data types and basic properties
        assert isinstance(roc_metrics['fpr'], np.ndarray)
        assert isinstance(roc_metrics['tpr'], np.ndarray)
        assert isinstance(roc_metrics['thresholds'], np.ndarray)
        assert isinstance(roc_metrics['threshold_metrics'], pd.DataFrame)
        
        # Check AUC is in valid range
        assert 0.0 <= roc_metrics['roc_auc'] <= 1.0
        
        # Check optimal metrics are in valid ranges
        assert 0.0 <= roc_metrics['optimal_tpr'] <= 1.0
        assert 0.0 <= roc_metrics['optimal_fpr'] <= 1.0
        assert -1.0 <= roc_metrics['optimal_youden_index'] <= 1.0
        
        # Check sample size
        assert roc_metrics['n_samples'] == 200
    
    def test_calculate_roc_metrics_with_custom_pos_label(self, binary_classification_data):
        """Test ROC metrics with custom positive label"""
        roc_metrics = calculate_roc_metrics(
            model=binary_classification_data['model'],
            X=binary_classification_data['X'],
            y=binary_classification_data['y'],
            cv=3,
            pos_label=0  # Use 0 as positive label instead of default 1
        )
        
        assert roc_metrics['pos_label'] == 0
        assert 0.0 <= roc_metrics['roc_auc'] <= 1.0
    
    def test_calculate_precision_recall_metrics(self, binary_classification_data):
        """Test Precision-Recall metrics calculation"""
        pr_metrics = calculate_precision_recall_metrics(
            model=binary_classification_data['model'],
            X=binary_classification_data['X'],
            y=binary_classification_data['y'],
            cv=3
        )
        
        # Check required components
        required_keys = [
            'precision', 'recall', 'thresholds', 'pr_auc',
            'optimal_threshold', 'optimal_precision', 'optimal_recall',
            'optimal_f1', 'y_scores', 'y_true', 'pos_label', 'n_samples'
        ]
        
        for key in required_keys:
            assert key in pr_metrics
        
        # Check data types
        assert isinstance(pr_metrics['precision'], np.ndarray)
        assert isinstance(pr_metrics['recall'], np.ndarray)
        assert isinstance(pr_metrics['thresholds'], np.ndarray)
        
        # Check metric ranges
        assert 0.0 <= pr_metrics['pr_auc'] <= 1.0
        assert 0.0 <= pr_metrics['optimal_precision'] <= 1.0
        assert 0.0 <= pr_metrics['optimal_recall'] <= 1.0
        assert 0.0 <= pr_metrics['optimal_f1'] <= 1.0
        
        # Check sample size
        assert pr_metrics['n_samples'] == 200
    
    def test_calculate_multiclass_roc_metrics(self, multiclass_classification_data):
        """Test multiclass ROC metrics calculation"""
        multiclass_metrics = calculate_multiclass_roc_metrics(
            model=multiclass_classification_data['model'],
            X=multiclass_classification_data['X'],
            y=multiclass_classification_data['y'],
            cv=3
        )
        
        # Check required components
        required_keys = [
            'class_results', 'micro_average', 'macro_average',
            'class_labels', 'n_classes', 'n_samples', 'y_proba', 'y_true'
        ]
        
        for key in required_keys:
            assert key in multiclass_metrics
        
        # Check number of classes
        assert multiclass_metrics['n_classes'] == 3
        assert len(multiclass_metrics['class_labels']) == 3
        assert len(multiclass_metrics['class_results']) == 3
        
        # Check micro and macro averages
        assert 0.0 <= multiclass_metrics['micro_average']['roc_auc'] <= 1.0
        assert 0.0 <= multiclass_metrics['macro_average']['roc_auc'] <= 1.0
        
        # Check per-class results
        for class_label in multiclass_metrics['class_labels']:
            class_data = multiclass_metrics['class_results'][class_label]
            assert 0.0 <= class_data['roc_auc'] <= 1.0
            assert 0.0 <= class_data['optimal_tpr'] <= 1.0
            assert 0.0 <= class_data['optimal_fpr'] <= 1.0
        
        # Check sample size
        assert multiclass_metrics['n_samples'] == 300
    
    def test_find_optimal_thresholds(self, binary_classification_data):
        """Test optimal threshold finding with different criteria"""
        roc_metrics = calculate_roc_metrics(
            model=binary_classification_data['model'],
            X=binary_classification_data['X'],
            y=binary_classification_data['y'],
            cv=3
        )
        
        # Test with default criteria
        optimal_df = find_optimal_thresholds(roc_metrics)
        
        # Check DataFrame structure
        assert isinstance(optimal_df, pd.DataFrame)
        expected_columns = ['Criterion', 'Description', 'Threshold', 'TPR (Sensitivity)', 
                           'FPR', 'TNR (Specificity)', 'Youden Index']
        assert list(optimal_df.columns) == expected_columns
        
        # Check that we have results for default criteria
        criteria_found = optimal_df['Criterion'].tolist()
        expected_criteria = ['Youden', 'Closest To Perfect', 'Balanced Accuracy']
        assert len(set(expected_criteria) & set(criteria_found)) == len(expected_criteria)
        
        # Check value ranges
        assert all(0.0 <= val <= 1.0 for val in optimal_df['TPR (Sensitivity)'])
        assert all(0.0 <= val <= 1.0 for val in optimal_df['FPR'])
        assert all(0.0 <= val <= 1.0 for val in optimal_df['TNR (Specificity)'])
        assert all(-1.0 <= val <= 1.0 for val in optimal_df['Youden Index'])
    
    def test_create_threshold_analysis_report(self, binary_classification_data):
        """Test threshold analysis report creation"""
        roc_metrics = calculate_roc_metrics(
            model=binary_classification_data['model'],
            X=binary_classification_data['X'],
            y=binary_classification_data['y'],
            cv=3
        )
        
        pr_metrics = calculate_precision_recall_metrics(
            model=binary_classification_data['model'],
            X=binary_classification_data['X'],
            y=binary_classification_data['y'],
            cv=3
        )
        
        # Test with both ROC and PR metrics
        report_df = create_threshold_analysis_report(roc_metrics, pr_metrics)
        
        # Check DataFrame structure
        assert isinstance(report_df, pd.DataFrame)
        expected_columns = ['Category', 'Metric', 'Value', 'Description']
        assert list(report_df.columns) == expected_columns
        
        # Check that we have expected categories
        categories = report_df['Category'].unique()
        assert 'ROC Analysis' in categories
        assert 'PR Analysis' in categories
        assert 'Sample Info' in categories
        
        # Test with ROC metrics only
        report_df_roc_only = create_threshold_analysis_report(roc_metrics)
        categories_roc_only = report_df_roc_only['Category'].unique()
        assert 'ROC Analysis' in categories_roc_only
        assert 'Sample Info' in categories_roc_only
        assert 'PR Analysis' not in categories_roc_only
    
    def test_print_roc_auc_summary(self, binary_classification_data, capsys):
        """Test printing of ROC/AUC summary"""
        roc_metrics = calculate_roc_metrics(
            model=binary_classification_data['model'],
            X=binary_classification_data['X'],
            y=binary_classification_data['y'],
            cv=3
        )
        
        pr_metrics = calculate_precision_recall_metrics(
            model=binary_classification_data['model'],
            X=binary_classification_data['X'],
            y=binary_classification_data['y'],
            cv=3
        )
        
        # Test with both ROC and PR metrics
        print_roc_auc_summary(roc_metrics, pr_metrics)
        
        captured = capsys.readouterr()
        assert "ROC CURVE AND AUC ANALYSIS REPORT" in captured.out
        assert "ROC CURVE ANALYSIS:" in captured.out
        assert "OPTIMAL THRESHOLD" in captured.out
        assert "PRECISION-RECALL ANALYSIS:" in captured.out
        assert "RECOMMENDATIONS:" in captured.out
        
        # Test with ROC metrics only
        print_roc_auc_summary(roc_metrics)
        
        captured_roc_only = capsys.readouterr()
        assert "ROC CURVE AND AUC ANALYSIS REPORT" in captured_roc_only.out
        assert "PRECISION-RECALL ANALYSIS:" not in captured_roc_only.out
    
    def test_different_cv_values(self, binary_classification_data):
        """Test ROC metrics with different CV values"""
        for cv in [3, 5, 10]:
            roc_metrics = calculate_roc_metrics(
                model=binary_classification_data['model'],
                X=binary_classification_data['X'],
                y=binary_classification_data['y'],
                cv=cv
            )
            
            assert roc_metrics['n_samples'] == 200
            assert 0.0 <= roc_metrics['roc_auc'] <= 1.0
    
    def test_pipeline_compatibility(self, binary_classification_data):
        """Test that ROC analysis works with pipelines"""
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('classifier', LogisticRegression(random_state=42))
        ])
        
        roc_metrics = calculate_roc_metrics(
            model=pipeline,
            X=binary_classification_data['X'],
            y=binary_classification_data['y'],
            cv=3
        )
        
        # Should work without error and return valid metrics
        assert 'roc_auc' in roc_metrics
        assert 0.0 <= roc_metrics['roc_auc'] <= 1.0
        assert roc_metrics['n_samples'] == 200
    
    def test_edge_case_perfect_classifier(self):
        """Test with perfectly separable data"""
        # Create perfectly separable data
        X = np.array([[0, 0], [1, 1], [0, 1], [1, 0], [0, 0.1], [1, 0.9]])
        y = np.array([0, 1, 0, 1, 0, 1])
        
        model = LogisticRegression(random_state=42)
        
        roc_metrics = calculate_roc_metrics(model, X, y, cv=3)
        
        # Perfect classifier should have high AUC
        assert roc_metrics['roc_auc'] > 0.9
        assert roc_metrics['n_samples'] == 6
    
    def test_error_handling_non_binary_for_binary_functions(self, multiclass_classification_data):
        """Test error handling when using binary functions on multiclass data"""
        with pytest.raises(ValueError, match="Binary classification expected"):
            calculate_roc_metrics(
                model=multiclass_classification_data['model'],
                X=multiclass_classification_data['X'],
                y=multiclass_classification_data['y'],
                cv=3
            )
        
        with pytest.raises(ValueError, match="Binary classification expected"):
            calculate_precision_recall_metrics(
                model=multiclass_classification_data['model'],
                X=multiclass_classification_data['X'],
                y=multiclass_classification_data['y'],
                cv=3
            )
    
    def test_error_handling_binary_for_multiclass_functions(self, binary_classification_data):
        """Test error handling when using multiclass functions on binary data"""
        with pytest.raises(ValueError, match="Multiclass classification expected"):
            calculate_multiclass_roc_metrics(
                model=binary_classification_data['model'],
                X=binary_classification_data['X'],
                y=binary_classification_data['y'],
                cv=3
            )
    
    def test_threshold_metrics_dataframe_structure(self, binary_classification_data):
        """Test that threshold metrics DataFrame has correct structure"""
        roc_metrics = calculate_roc_metrics(
            model=binary_classification_data['model'],
            X=binary_classification_data['X'],
            y=binary_classification_data['y'],
            cv=3
        )
        
        threshold_df = roc_metrics['threshold_metrics']
        
        # Check columns
        expected_columns = [
            'threshold', 'fpr', 'tpr', 'tnr', 'fnr', 
            'youden_index', 'distance_to_perfect'
        ]
        assert list(threshold_df.columns) == expected_columns
        
        # Check value ranges
        assert all(0.0 <= val <= 1.0 for val in threshold_df['fpr'])
        assert all(0.0 <= val <= 1.0 for val in threshold_df['tpr'])
        assert all(0.0 <= val <= 1.0 for val in threshold_df['tnr'])
        assert all(0.0 <= val <= 1.0 for val in threshold_df['fnr'])
        assert all(-1.0 <= val <= 1.0 for val in threshold_df['youden_index'])
        assert all(0.0 <= val <= np.sqrt(2) for val in threshold_df['distance_to_perfect'])
    
    def test_small_sample_handling(self):
        """Test handling of small samples"""
        # Create very small dataset
        X = np.random.randn(20, 3)
        y = np.random.choice([0, 1], size=20)
        model = LogisticRegression(random_state=42)
        
        roc_metrics = calculate_roc_metrics(model, X, y, cv=3)
        
        assert roc_metrics['n_samples'] == 20
        assert 'roc_auc' in roc_metrics
    
    def test_string_labels(self):
        """Test with string class labels"""
        X, y_numeric = make_classification(n_samples=100, n_features=4, 
                                          n_classes=2, random_state=42)
        
        # Convert to string labels
        y = np.array(['negative' if label == 0 else 'positive' for label in y_numeric])
        
        model = LogisticRegression(random_state=42)
        
        roc_metrics = calculate_roc_metrics(model, X, y, cv=3, pos_label='positive')
        
        assert roc_metrics['pos_label'] == 'positive'
        assert 0.0 <= roc_metrics['roc_auc'] <= 1.0
        assert roc_metrics['n_samples'] == 100