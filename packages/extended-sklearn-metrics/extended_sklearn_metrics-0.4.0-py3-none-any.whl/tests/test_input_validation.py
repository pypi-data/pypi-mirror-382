import pytest
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.datasets import make_regression
from sklearn.svm import SVC  # Classification model for testing warnings
from extended_sklearn_metrics import evaluate_model_with_cross_validation
import warnings


class TestInputValidation:
    """Test suite for input validation"""
    
    @pytest.fixture
    def valid_data(self):
        """Create valid test data"""
        X, y = make_regression(n_samples=50, n_features=3, noise=0.1, random_state=42)
        return {
            'X': X,
            'y': y,
            'model': LinearRegression()
        }
    
    def test_invalid_model_no_fit(self, valid_data):
        """Test error when model doesn't have fit method"""
        class InvalidModel:
            def predict(self, X):
                pass
        
        with pytest.raises(ValueError, match="Model must have 'fit' and 'predict' methods"):
            evaluate_model_with_cross_validation(
                model=InvalidModel(),
                X=valid_data['X'],
                y=valid_data['y']
            )
    
    def test_invalid_model_no_predict(self, valid_data):
        """Test error when model doesn't have predict method"""
        class InvalidModel:
            def fit(self, X, y):
                pass
        
        with pytest.raises(ValueError, match="Model must have 'fit' and 'predict' methods"):
            evaluate_model_with_cross_validation(
                model=InvalidModel(),
                X=valid_data['X'],
                y=valid_data['y']
            )
    
    def test_empty_X(self, valid_data):
        """Test error with empty X"""
        with pytest.raises(ValueError, match="X cannot be empty"):
            evaluate_model_with_cross_validation(
                model=valid_data['model'],
                X=np.array([]).reshape(0, 3),
                y=valid_data['y']
            )
    
    def test_empty_y(self, valid_data):
        """Test error with empty y"""
        with pytest.raises(ValueError, match="y cannot be empty"):
            evaluate_model_with_cross_validation(
                model=valid_data['model'],
                X=valid_data['X'],
                y=np.array([])
            )
    
    def test_wrong_X_dimensions(self, valid_data):
        """Test error with wrong X dimensions"""
        # 1D X
        with pytest.raises(ValueError, match="X must be 2-dimensional, got 1 dimensions"):
            evaluate_model_with_cross_validation(
                model=valid_data['model'],
                X=valid_data['X'][:, 0],  # 1D array
                y=valid_data['y']
            )
        
        # 3D X
        with pytest.raises(ValueError, match="X must be 2-dimensional, got 3 dimensions"):
            evaluate_model_with_cross_validation(
                model=valid_data['model'],
                X=valid_data['X'].reshape(5, 10, 3),
                y=valid_data['y']
            )
    
    def test_wrong_y_dimensions(self, valid_data):
        """Test error with wrong y dimensions"""
        with pytest.raises(ValueError, match="y must be 1-dimensional, got 2 dimensions"):
            evaluate_model_with_cross_validation(
                model=valid_data['model'],
                X=valid_data['X'],
                y=valid_data['y'].reshape(-1, 1)  # 2D array
            )
    
    def test_mismatched_lengths(self, valid_data):
        """Test error with mismatched X and y lengths"""
        with pytest.raises(ValueError, match="X and y must have same number of samples"):
            evaluate_model_with_cross_validation(
                model=valid_data['model'],
                X=valid_data['X'][:30],  # 30 samples
                y=valid_data['y'][:40]   # 40 samples
            )
    
    def test_invalid_cv_values(self, valid_data):
        """Test error with invalid cv values"""
        # cv < 2
        with pytest.raises(ValueError, match="cv must be an integer >= 2"):
            evaluate_model_with_cross_validation(
                model=valid_data['model'],
                X=valid_data['X'],
                y=valid_data['y'],
                cv=1
            )
        
        # cv > number of samples
        with pytest.raises(ValueError, match="cv \\(60\\) cannot be greater than number of samples"):
            evaluate_model_with_cross_validation(
                model=valid_data['model'],
                X=valid_data['X'],
                y=valid_data['y'],
                cv=60  # More than 50 samples
            )
        
        # Non-integer cv
        with pytest.raises(ValueError, match="cv must be an integer >= 2"):
            evaluate_model_with_cross_validation(
                model=valid_data['model'],
                X=valid_data['X'],
                y=valid_data['y'],
                cv=3.5
            )
    
    def test_nan_values_in_X(self, valid_data):
        """Test error with NaN values in X"""
        X_with_nan = valid_data['X'].copy()
        X_with_nan[0, 0] = np.nan
        
        with pytest.raises(ValueError, match="X contains NaN or infinite values"):
            evaluate_model_with_cross_validation(
                model=valid_data['model'],
                X=X_with_nan,
                y=valid_data['y']
            )
    
    def test_inf_values_in_X(self, valid_data):
        """Test error with infinite values in X"""
        X_with_inf = valid_data['X'].copy()
        X_with_inf[0, 0] = np.inf
        
        with pytest.raises(ValueError, match="X contains NaN or infinite values"):
            evaluate_model_with_cross_validation(
                model=valid_data['model'],
                X=X_with_inf,
                y=valid_data['y']
            )
    
    def test_nan_values_in_y(self, valid_data):
        """Test error with NaN values in y"""
        y_with_nan = valid_data['y'].copy()
        y_with_nan[0] = np.nan
        
        with pytest.raises(ValueError, match="y contains NaN or infinite values"):
            evaluate_model_with_cross_validation(
                model=valid_data['model'],
                X=valid_data['X'],
                y=y_with_nan
            )
    
    def test_inf_values_in_y(self, valid_data):
        """Test error with infinite values in y"""
        y_with_inf = valid_data['y'].copy()
        y_with_inf[0] = np.inf
        
        with pytest.raises(ValueError, match="y contains NaN or infinite values"):
            evaluate_model_with_cross_validation(
                model=valid_data['model'],
                X=valid_data['X'],
                y=y_with_inf
            )
    
    def test_invalid_target_range(self, valid_data):
        """Test error with invalid target_range values"""
        # Negative target_range
        with pytest.raises(ValueError, match="target_range must be a positive number"):
            evaluate_model_with_cross_validation(
                model=valid_data['model'],
                X=valid_data['X'],
                y=valid_data['y'],
                target_range=-1.0
            )
        
        # Zero target_range
        with pytest.raises(ValueError, match="target_range must be a positive number"):
            evaluate_model_with_cross_validation(
                model=valid_data['model'],
                X=valid_data['X'],
                y=valid_data['y'],
                target_range=0.0
            )
    
    def test_zero_variance_warning(self, valid_data):
        """Test warning with zero variance in y"""
        y_constant = np.ones(len(valid_data['y']))
        
        with pytest.warns(UserWarning, match="Target variable has zero variance"):
            result = evaluate_model_with_cross_validation(
                model=valid_data['model'],
                X=valid_data['X'],
                y=y_constant
            )
        
        # Should still work, just with warning
        assert isinstance(result, pd.DataFrame)
    
    def test_classification_model_warning(self, valid_data):
        """Test warning when using classification model"""
        from sklearn.base import BaseEstimator
        
        # Create a mock classifier that has the right attributes but works with regression data
        class MockClassifier(BaseEstimator):
            _estimator_type = 'classifier'
            
            def fit(self, X, y):
                return self
            
            def predict(self, X):
                return np.ones(len(X))  # Simple prediction
        
        classifier = MockClassifier()
        
        with pytest.warns(UserWarning, match="Model appears to be a 'classifier'"):
            result = evaluate_model_with_cross_validation(
                model=classifier,
                X=valid_data['X'],
                y=valid_data['y'],
                cv=3
            )
        
        # Should still work, just with warning
        assert isinstance(result, pd.DataFrame)
    
    def test_pandas_input_types(self, valid_data):
        """Test that pandas DataFrames and Series work correctly"""
        X_df = pd.DataFrame(valid_data['X'], columns=[f'feature_{i}' for i in range(3)])
        y_series = pd.Series(valid_data['y'])
        
        # Should work without error
        result = evaluate_model_with_cross_validation(
            model=valid_data['model'],
            X=X_df,
            y=y_series,
            cv=3
        )
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 4
    
    def test_minimum_samples_edge_case(self):
        """Test edge case with minimum number of samples"""
        # Create minimal dataset
        X = np.array([[1, 2], [3, 4], [5, 6], [7, 8]])  # 4 samples
        y = np.array([1, 2, 3, 4])
        model = LinearRegression()
        
        # Should work with cv=2 (minimum)
        result = evaluate_model_with_cross_validation(
            model=model,
            X=X,
            y=y,
            cv=2
        )
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 4