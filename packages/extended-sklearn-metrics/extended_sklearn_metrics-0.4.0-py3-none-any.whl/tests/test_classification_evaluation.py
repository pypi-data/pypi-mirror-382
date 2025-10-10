import pytest
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.datasets import make_classification
from extended_sklearn_metrics import evaluate_classification_model_with_cross_validation


class TestClassificationEvaluation:
    """Test suite for classification evaluation"""
    
    @pytest.fixture
    def binary_data(self):
        """Create binary classification test data"""
        X, y = make_classification(
            n_samples=200,
            n_features=4,
            n_classes=2,
            n_redundant=0,
            random_state=42
        )
        return {
            'X': pd.DataFrame(X, columns=[f'feature_{i}' for i in range(4)]),
            'y': pd.Series(y),
            'model': LogisticRegression(random_state=42, max_iter=1000)
        }
    
    @pytest.fixture
    def multiclass_data(self):
        """Create multiclass classification test data"""
        X, y = make_classification(
            n_samples=300,
            n_features=5,
            n_classes=3,
            n_redundant=0,
            n_informative=3,
            random_state=42
        )
        return {
            'X': pd.DataFrame(X, columns=[f'feature_{i}' for i in range(5)]),
            'y': pd.Series(y),
            'model': RandomForestClassifier(n_estimators=10, random_state=42)
        }
    
    def test_binary_classification_output_format(self, binary_data):
        """Test binary classification output format"""
        result = evaluate_classification_model_with_cross_validation(
            model=binary_data['model'],
            X=binary_data['X'],
            y=binary_data['y'],
            cv=3
        )
        
        # Check DataFrame structure
        expected_columns = ['Metric', 'Value', 'Threshold', 'Calculation', 'Performance']
        assert list(result.columns) == expected_columns
        
        # Check metrics are present (binary should include ROC AUC)
        expected_metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC AUC']
        assert list(result['Metric']) == expected_metrics
        
        # Check number of rows
        assert len(result) == 5
    
    def test_multiclass_classification_output_format(self, multiclass_data):
        """Test multiclass classification output format"""
        result = evaluate_classification_model_with_cross_validation(
            model=multiclass_data['model'],
            X=multiclass_data['X'],
            y=multiclass_data['y'],
            cv=3
        )
        
        # Check DataFrame structure
        expected_columns = ['Metric', 'Value', 'Threshold', 'Calculation', 'Performance']
        assert list(result.columns) == expected_columns
        
        # Check metrics are present (multiclass should NOT include ROC AUC)
        expected_metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
        assert list(result['Metric']) == expected_metrics
        
        # Check number of rows
        assert len(result) == 4
    
    def test_performance_categories(self, binary_data):
        """Test that performance categories are correctly assigned"""
        result = evaluate_classification_model_with_cross_validation(
            model=binary_data['model'],
            X=binary_data['X'],
            y=binary_data['y'],
            cv=3
        )
        
        # Check that performance categories are valid
        valid_categories = {'Excellent', 'Good', 'Acceptable', 'Poor', 'Very Poor'}
        for performance in result['Performance']:
            assert performance in valid_categories
    
    def test_metric_value_ranges(self, binary_data):
        """Test that metric values are within expected ranges"""
        result = evaluate_classification_model_with_cross_validation(
            model=binary_data['model'],
            X=binary_data['X'],
            y=binary_data['y'],
            cv=3
        )
        
        # All classification metrics should be between 0 and 1
        for value in result['Value']:
            assert 0 <= value <= 1
    
    def test_different_averaging_strategies(self, multiclass_data):
        """Test different averaging strategies for multiclass"""
        averaging_strategies = ['weighted', 'macro', 'micro']
        
        for avg_strategy in averaging_strategies:
            result = evaluate_classification_model_with_cross_validation(
                model=multiclass_data['model'],
                X=multiclass_data['X'],
                y=multiclass_data['y'],
                cv=3,
                average=avg_strategy
            )
            
            # Should complete without error
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 4  # No ROC AUC for multiclass
            
            # Check that averaging strategy is mentioned in calculations
            precision_calc = result.loc[result['Metric'] == 'Precision', 'Calculation'].iloc[0]
            assert avg_strategy in precision_calc
    
    def test_different_input_types(self, binary_data):
        """Test function works with different input types"""
        # Test with numpy arrays
        X_numpy = binary_data['X'].to_numpy()
        y_numpy = binary_data['y'].to_numpy()
        
        result_numpy = evaluate_classification_model_with_cross_validation(
            model=binary_data['model'],
            X=X_numpy,
            y=y_numpy,
            cv=3
        )
        
        assert isinstance(result_numpy, pd.DataFrame)
        
        # Test with pandas objects
        result_pandas = evaluate_classification_model_with_cross_validation(
            model=binary_data['model'],
            X=binary_data['X'],
            y=binary_data['y'],
            cv=3
        )
        
        assert isinstance(result_pandas, pd.DataFrame)
    
    def test_different_cv_folds(self, binary_data):
        """Test function works with different CV fold numbers"""
        for cv_folds in [3, 5]:
            result = evaluate_classification_model_with_cross_validation(
                model=binary_data['model'],
                X=binary_data['X'],
                y=binary_data['y'],
                cv=cv_folds
            )
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 5  # Binary classification metrics
    
    def test_various_classifiers(self, binary_data):
        """Test function works with different classifier types"""
        classifiers = [
            LogisticRegression(random_state=42, max_iter=1000),
            RandomForestClassifier(n_estimators=10, random_state=42),
            SVC(probability=True, random_state=42)  # probability=True for ROC AUC
        ]
        
        for clf in classifiers:
            result = evaluate_classification_model_with_cross_validation(
                model=clf,
                X=binary_data['X'],
                y=binary_data['y'],
                cv=3
            )
            
            # Each should work without error
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 5  # Binary classification metrics
    
    def test_input_validation_errors(self, binary_data):
        """Test input validation for classification"""
        # Test invalid CV
        with pytest.raises(ValueError, match="cv must be an integer >= 2"):
            evaluate_classification_model_with_cross_validation(
                model=binary_data['model'],
                X=binary_data['X'],
                y=binary_data['y'],
                cv=1
            )
        
        # Test mismatched lengths
        with pytest.raises(ValueError, match="X and y must have same number of samples"):
            evaluate_classification_model_with_cross_validation(
                model=binary_data['model'],
                X=binary_data['X'].iloc[:100],
                y=binary_data['y'].iloc[:150]
            )
        
        # Test empty data
        with pytest.raises(ValueError, match="X cannot be empty"):
            evaluate_classification_model_with_cross_validation(
                model=binary_data['model'],
                X=pd.DataFrame(),
                y=binary_data['y']
            )
    
    def test_regression_model_warning(self, binary_data):
        """Test warning when using regression model"""
        from sklearn.base import BaseEstimator
        
        class MockRegressor(BaseEstimator):
            _estimator_type = 'regressor'
            
            def fit(self, X, y):
                return self
            
            def predict(self, X):
                return np.random.randint(0, 2, len(X))  # Random binary predictions
        
        regressor = MockRegressor()
        
        # Use simpler data to avoid ROC AUC issues with mock regressor
        X_simple = binary_data['X'].iloc[:50]  # Smaller dataset
        y_simple = binary_data['y'].iloc[:50]
        
        with pytest.warns(UserWarning, match="Model appears to be a 'regressor'"):
            # Note: This may fail on ROC AUC since our mock doesn't have predict_proba
            # So we'll catch any sklearn scoring errors and just test the warning
            try:
                result = evaluate_classification_model_with_cross_validation(
                    model=regressor,
                    X=X_simple,
                    y=y_simple,
                    cv=2  # Reduce CV folds for stability
                )
                assert isinstance(result, pd.DataFrame)
            except (ValueError, AttributeError):
                # If sklearn complains about scoring methods, that's okay
                # We just wanted to test that our warning is triggered
                pass
        
        # Test passed if we get here without error
    
    def test_string_labels(self):
        """Test classification with string labels"""
        X, y_numeric = make_classification(
            n_samples=100,
            n_features=5,
            n_classes=3,
            n_informative=3,
            n_redundant=0,
            random_state=42
        )
        
        # Convert numeric labels to strings
        label_map = {0: 'class_A', 1: 'class_B', 2: 'class_C'}
        y_string = pd.Series([label_map[label] for label in y_numeric])
        
        model = LogisticRegression(random_state=42, max_iter=1000)
        
        result = evaluate_classification_model_with_cross_validation(
            model=model,
            X=X,
            y=y_string,
            cv=3
        )
        
        # Should work with string labels
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 4  # Multiclass (no ROC AUC)
    
    def test_minimum_samples_edge_case(self):
        """Test edge case with minimum number of samples"""
        # Create minimal dataset
        X = np.array([[1, 2], [3, 4], [5, 6], [7, 8]])  # 4 samples
        y = np.array([0, 1, 0, 1])  # Binary classification
        model = LogisticRegression(random_state=42, max_iter=1000)
        
        # Should work with cv=2 (minimum)
        result = evaluate_classification_model_with_cross_validation(
            model=model,
            X=X,
            y=y,
            cv=2
        )
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 5  # Binary classification metrics