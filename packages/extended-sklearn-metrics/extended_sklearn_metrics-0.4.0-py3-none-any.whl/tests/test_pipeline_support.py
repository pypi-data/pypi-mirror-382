import pytest
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.datasets import make_regression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, PolynomialFeatures, OneHotEncoder
from sklearn.compose import ColumnTransformer
from extended_sklearn_metrics import evaluate_model_with_cross_validation


class TestPipelineSupport:
    """Test suite for pipeline compatibility"""
    
    @pytest.fixture
    def numeric_data(self):
        """Create numeric test data"""
        X, y = make_regression(
            n_samples=100,
            n_features=5,
            noise=0.1,
            random_state=42
        )
        return {
            'X': pd.DataFrame(X, columns=[f'feature_{i}' for i in range(5)]),
            'y': pd.Series(y),
            'target_range': np.max(y) - np.min(y)
        }
    
    @pytest.fixture
    def mixed_data(self):
        """Create mixed numeric/categorical test data"""
        X_num, y = make_regression(
            n_samples=150,
            n_features=4,
            noise=0.1,
            random_state=42
        )
        X_cat = np.random.choice(['A', 'B', 'C'], size=(150, 2))
        
        X = pd.DataFrame(X_num, columns=[f'num_{i}' for i in range(4)])
        for i in range(2):
            X[f'cat_{i}'] = X_cat[:, i]
        
        return {
            'X': X,
            'y': pd.Series(y),
            'target_range': np.max(y) - np.min(y)
        }
    
    def test_basic_pipeline(self, numeric_data):
        """Test basic pipeline with preprocessing"""
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('regressor', LinearRegression())
        ])
        
        result = evaluate_model_with_cross_validation(
            model=pipeline,
            X=numeric_data['X'],
            y=numeric_data['y'],
            cv=3,
            target_range=numeric_data['target_range']
        )
        
        # Check that result is properly formatted
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 4
        assert 'Performance' in result.columns
        
        # Check that R² is reasonable for a simple linear model
        r2_value = result.loc[result['Metric'] == 'R²', 'Value'].iloc[0]
        assert r2_value > 0.5  # Should be decent for synthetic data
    
    def test_complex_pipeline(self, mixed_data):
        """Test complex pipeline with ColumnTransformer"""
        preprocessor = ColumnTransformer([
            ('num', StandardScaler(), [f'num_{i}' for i in range(4)]),
            ('cat', OneHotEncoder(drop='first'), [f'cat_{i}' for i in range(2)])
        ])
        
        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('regressor', Ridge(alpha=1.0))
        ])
        
        result = evaluate_model_with_cross_validation(
            model=pipeline,
            X=mixed_data['X'],
            y=mixed_data['y'],
            cv=3,
            target_range=mixed_data['target_range']
        )
        
        # Verify structure
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 4
        
        # Check that metrics are computed
        for metric in ['RMSE', 'MAE', 'R²', 'Explained Variance']:
            metric_row = result[result['Metric'] == metric]
            assert len(metric_row) == 1
            assert not pd.isna(metric_row['Value'].iloc[0])
    
    def test_ensemble_pipeline(self, numeric_data):
        """Test pipeline with ensemble method"""
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('regressor', RandomForestRegressor(n_estimators=10, random_state=42))
        ])
        
        result = evaluate_model_with_cross_validation(
            model=pipeline,
            X=numeric_data['X'],
            y=numeric_data['y'],
            cv=3,
            target_range=numeric_data['target_range']
        )
        
        # Random Forest should perform reasonably well
        r2_value = result.loc[result['Metric'] == 'R²', 'Value'].iloc[0]
        assert r2_value > 0.5  # RF should be decent on synthetic data
    
    def test_polynomial_pipeline(self, numeric_data):
        """Test pipeline with polynomial features"""
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('poly', PolynomialFeatures(degree=2, include_bias=False)),
            ('regressor', Ridge(alpha=1.0))  # Ridge to handle multicollinearity
        ])
        
        # Use smaller dataset to avoid overfitting
        X_small = numeric_data['X'].iloc[:50]
        y_small = numeric_data['y'].iloc[:50]
        
        result = evaluate_model_with_cross_validation(
            model=pipeline,
            X=X_small,
            y=y_small,
            cv=3
        )
        
        # Should complete without error
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 4
    
    def test_pipeline_performance_categories(self, numeric_data):
        """Test that performance categories are assigned correctly for pipelines"""
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('regressor', LinearRegression())
        ])
        
        result = evaluate_model_with_cross_validation(
            model=pipeline,
            X=numeric_data['X'],
            y=numeric_data['y'],
            cv=3,
            target_range=numeric_data['target_range']
        )
        
        # Check performance categories are valid
        valid_categories = {'Excellent', 'Good', 'Moderate', 'Poor', 'Acceptable'}
        for performance in result['Performance']:
            assert performance in valid_categories
    
    def test_pipeline_with_different_cv_folds(self, numeric_data):
        """Test pipeline works with different CV fold numbers"""
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('regressor', LinearRegression())
        ])
        
        # Test different CV values
        for cv_folds in [3, 5]:
            result = evaluate_model_with_cross_validation(
                model=pipeline,
                X=numeric_data['X'],
                y=numeric_data['y'],
                cv=cv_folds,
                target_range=numeric_data['target_range']
            )
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 4
    
    def test_pipeline_without_target_range(self, numeric_data):
        """Test pipeline works when target_range is not provided"""
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('regressor', LinearRegression())
        ])
        
        result = evaluate_model_with_cross_validation(
            model=pipeline,
            X=numeric_data['X'],
            y=numeric_data['y'],
            cv=3
            # Note: target_range not provided
        )
        
        # Should auto-calculate and work fine
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 4
        
        # Check that calculations use auto-computed range
        expected_range = np.max(numeric_data['y']) - np.min(numeric_data['y'])
        rmse_calc = result.loc[result['Metric'] == 'RMSE', 'Calculation'].iloc[0]
        assert f'{expected_range:.2f}' in rmse_calc
    
    def test_multiple_pipeline_types(self, numeric_data):
        """Test multiple different pipeline configurations"""
        pipelines = [
            # Simple preprocessing
            Pipeline([
                ('scaler', StandardScaler()),
                ('regressor', LinearRegression())
            ]),
            # No preprocessing
            Pipeline([
                ('regressor', LinearRegression())
            ]),
            # Multiple preprocessing steps
            Pipeline([
                ('scaler', StandardScaler()),
                ('poly', PolynomialFeatures(degree=2, include_bias=False)),
                ('regressor', Ridge(alpha=10.0))
            ])
        ]
        
        for i, pipeline in enumerate(pipelines):
            result = evaluate_model_with_cross_validation(
                model=pipeline,
                X=numeric_data['X'].iloc[:60],  # Smaller data for complex models
                y=numeric_data['y'].iloc[:60],
                cv=3
            )
            
            # Each should work without error
            assert isinstance(result, pd.DataFrame), f"Pipeline {i} failed"
            assert len(result) == 4, f"Pipeline {i} returned wrong number of metrics"