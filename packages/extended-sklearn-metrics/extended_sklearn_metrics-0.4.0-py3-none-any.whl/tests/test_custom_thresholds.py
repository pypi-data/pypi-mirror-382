import pytest
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.datasets import make_regression
from extended_sklearn_metrics import evaluate_model_with_cross_validation, CustomThresholds


class TestCustomThresholds:
    """Test suite for custom threshold functionality"""
    
    @pytest.fixture
    def test_data(self):
        """Create test data"""
        X, y = make_regression(n_samples=100, n_features=3, noise=0.1, random_state=42)
        return {
            'X': pd.DataFrame(X, columns=[f'feature_{i}' for i in range(3)]),
            'y': pd.Series(y),
            'model': LinearRegression()
        }
    
    def test_default_thresholds(self, test_data):
        """Test that default thresholds work as before"""
        result = evaluate_model_with_cross_validation(
            model=test_data['model'],
            X=test_data['X'],
            y=test_data['y'],
            cv=3
        )
        
        # Check that default threshold descriptions are present
        rmse_threshold = result.loc[result['Metric'] == 'RMSE', 'Threshold'].iloc[0]
        assert '<10% = Excellent' in rmse_threshold
        assert '10-20% = Good' in rmse_threshold
        assert '20-30% = Moderate' in rmse_threshold
        assert '>30% = Poor' in rmse_threshold
        
        r2_threshold = result.loc[result['Metric'] == 'R²', 'Threshold'].iloc[0]
        assert '> 0.7 = Good' in r2_threshold
        assert '0.5–0.7 = Acceptable' in r2_threshold
        assert '< 0.5 = Poor' in r2_threshold
    
    def test_custom_error_thresholds(self, test_data):
        """Test custom error thresholds for RMSE and MAE"""
        custom_thresholds = CustomThresholds(
            error_thresholds=(5, 15, 25),  # More strict thresholds
            score_thresholds=(0.5, 0.7)   # Keep score thresholds same
        )
        
        result = evaluate_model_with_cross_validation(
            model=test_data['model'],
            X=test_data['X'],
            y=test_data['y'],
            cv=3,
            custom_thresholds=custom_thresholds
        )
        
        # Check that custom error thresholds are reflected in descriptions
        rmse_threshold = result.loc[result['Metric'] == 'RMSE', 'Threshold'].iloc[0]
        assert '<5% = Excellent' in rmse_threshold
        assert '5-15% = Good' in rmse_threshold
        assert '15-25% = Moderate' in rmse_threshold
        assert '>25% = Poor' in rmse_threshold
        
        mae_threshold = result.loc[result['Metric'] == 'MAE', 'Threshold'].iloc[0]
        assert '<5% = Excellent' in mae_threshold
    
    def test_custom_score_thresholds(self, test_data):
        """Test custom score thresholds for R² and Explained Variance"""
        custom_thresholds = CustomThresholds(
            error_thresholds=(10, 20, 30),  # Keep error thresholds same
            score_thresholds=(0.6, 0.8)     # More strict score thresholds
        )
        
        result = evaluate_model_with_cross_validation(
            model=test_data['model'],
            X=test_data['X'],
            y=test_data['y'],
            cv=3,
            custom_thresholds=custom_thresholds
        )
        
        # Check that custom score thresholds are reflected
        r2_threshold = result.loc[result['Metric'] == 'R²', 'Threshold'].iloc[0]
        assert '> 0.8 = Good' in r2_threshold
        assert '0.6–0.8 = Acceptable' in r2_threshold
        assert '< 0.6 = Poor' in r2_threshold
        
        exp_var_threshold = result.loc[result['Metric'] == 'Explained Variance', 'Threshold'].iloc[0]
        assert '> 0.8 = Good' in exp_var_threshold
    
    def test_custom_thresholds_affect_performance_categories(self, test_data):
        """Test that custom thresholds actually affect performance categorization"""
        # Use very lenient thresholds
        lenient_thresholds = CustomThresholds(
            error_thresholds=(50, 70, 90),  # Very lenient for errors
            score_thresholds=(0.1, 0.3)     # Very lenient for scores
        )
        
        # Use very strict thresholds  
        strict_thresholds = CustomThresholds(
            error_thresholds=(1, 2, 3),     # Very strict for errors
            score_thresholds=(0.9, 0.95)    # Very strict for scores
        )
        
        # Get results with both threshold sets
        result_lenient = evaluate_model_with_cross_validation(
            model=test_data['model'],
            X=test_data['X'],
            y=test_data['y'],
            cv=3,
            custom_thresholds=lenient_thresholds
        )
        
        result_strict = evaluate_model_with_cross_validation(
            model=test_data['model'],
            X=test_data['X'],
            y=test_data['y'],
            cv=3,
            custom_thresholds=strict_thresholds
        )
        
        # With lenient thresholds, performance should generally be better
        lenient_rmse_perf = result_lenient.loc[result_lenient['Metric'] == 'RMSE', 'Performance'].iloc[0]
        strict_rmse_perf = result_strict.loc[result_strict['Metric'] == 'RMSE', 'Performance'].iloc[0]
        
        # With synthetic data and good model, lenient should give better rating
        performance_order = ['Poor', 'Moderate', 'Good', 'Excellent']
        lenient_idx = performance_order.index(lenient_rmse_perf) if lenient_rmse_perf in performance_order else -1
        strict_idx = performance_order.index(strict_rmse_perf) if strict_rmse_perf in performance_order else -1
        
        # Lenient should generally be better (higher index) than strict
        if lenient_idx >= 0 and strict_idx >= 0:
            assert lenient_idx >= strict_idx
    
    def test_custom_thresholds_class_initialization(self):
        """Test CustomThresholds class initialization"""
        # Test default initialization
        default_thresholds = CustomThresholds()
        assert default_thresholds.error_thresholds == (10, 20, 30)
        assert default_thresholds.score_thresholds == (0.5, 0.7)
        
        # Test custom initialization
        custom_thresholds = CustomThresholds(
            error_thresholds=(5, 10, 15),
            score_thresholds=(0.4, 0.8)
        )
        assert custom_thresholds.error_thresholds == (5, 10, 15)
        assert custom_thresholds.score_thresholds == (0.4, 0.8)
    
    def test_extreme_thresholds(self, test_data):
        """Test with extreme threshold values"""
        # Very easy thresholds (everything should be excellent)
        easy_thresholds = CustomThresholds(
            error_thresholds=(100, 200, 300),
            score_thresholds=(0.0, 0.1)
        )
        
        result = evaluate_model_with_cross_validation(
            model=test_data['model'],
            X=test_data['X'],
            y=test_data['y'],
            cv=3,
            custom_thresholds=easy_thresholds
        )
        
        # With synthetic regression data, errors should be low and scores high
        # So with easy thresholds, most metrics should perform well
        rmse_perf = result.loc[result['Metric'] == 'RMSE', 'Performance'].iloc[0]
        r2_perf = result.loc[result['Metric'] == 'R²', 'Performance'].iloc[0]
        
        # Should get good performance ratings
        assert rmse_perf in ['Excellent', 'Good', 'Moderate']
        assert r2_perf in ['Good', 'Acceptable']
    
    def test_thresholds_with_pipeline(self, test_data):
        """Test that custom thresholds work with pipelines"""
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import StandardScaler
        
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('regressor', LinearRegression())
        ])
        
        custom_thresholds = CustomThresholds(
            error_thresholds=(8, 16, 24),
            score_thresholds=(0.55, 0.75)
        )
        
        result = evaluate_model_with_cross_validation(
            model=pipeline,
            X=test_data['X'],
            y=test_data['y'],
            cv=3,
            custom_thresholds=custom_thresholds
        )
        
        # Check that custom thresholds are applied
        rmse_threshold = result.loc[result['Metric'] == 'RMSE', 'Threshold'].iloc[0]
        assert '<8% = Excellent' in rmse_threshold
        
        r2_threshold = result.loc[result['Metric'] == 'R²', 'Threshold'].iloc[0]
        assert '> 0.75 = Good' in r2_threshold
    
    def test_threshold_edge_cases(self, test_data):
        """Test edge cases for threshold values"""
        # Test with same values (edge case)
        edge_thresholds = CustomThresholds(
            error_thresholds=(10, 10, 10),  # All same
            score_thresholds=(0.5, 0.5)     # Same values
        )
        
        # Should still work without error
        result = evaluate_model_with_cross_validation(
            model=test_data['model'],
            X=test_data['X'],
            y=test_data['y'],
            cv=3,
            custom_thresholds=edge_thresholds
        )
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 4