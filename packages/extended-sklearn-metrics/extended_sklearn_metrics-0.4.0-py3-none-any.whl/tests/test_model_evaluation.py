import pytest
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.datasets import make_regression
from extended_sklearn_metrics import evaluate_model_with_cross_validation

@pytest.fixture
def test_data():
    """Create test data for all tests"""
    X, y = make_regression(
        n_samples=100,
        n_features=5,
        noise=0.1,
        random_state=42
    )
    return {
        'X': pd.DataFrame(X),
        'y': pd.Series(y),
        'model': LinearRegression(),
        'target_range': np.max(y) - np.min(y)
    }

def test_output_format(test_data):
    """Test if the output DataFrame has the correct format"""
    result = evaluate_model_with_cross_validation(
        model=test_data['model'],
        X=test_data['X'],
        y=test_data['y'],
        cv=5,
        target_range=test_data['target_range']
    )
    
    # Check DataFrame structure
    expected_columns = ['Metric', 'Value', 'Threshold', 'Calculation', 'Performance']
    assert list(result.columns) == expected_columns
    
    # Check metrics are present
    expected_metrics = ['RMSE', 'MAE', 'R²', 'Explained Variance']
    assert list(result['Metric']) == expected_metrics
    
    # Check number of rows
    assert len(result) == 4

def test_performance_categories(test_data):
    """Test if performance categories are correctly assigned"""
    result = evaluate_model_with_cross_validation(
        model=test_data['model'],
        X=test_data['X'],
        y=test_data['y'],
        cv=5,
        target_range=test_data['target_range']
    )
    
    # Check that performance categories are valid
    valid_categories = {'Excellent', 'Good', 'Moderate', 'Poor', 'Acceptable'}
    for performance in result['Performance']:
        assert performance in valid_categories

def test_value_ranges(test_data):
    """Test if metric values are within expected ranges"""
    result = evaluate_model_with_cross_validation(
        model=test_data['model'],
        X=test_data['X'],
        y=test_data['y'],
        cv=5,
        target_range=test_data['target_range']
    )
    
    # R² and Explained Variance should be between 0 and 1
    r2_idx = result['Metric'] == 'R²'
    exp_var_idx = result['Metric'] == 'Explained Variance'
    
    assert 0 <= result.loc[r2_idx, 'Value'].iloc[0] <= 1
    assert 0 <= result.loc[exp_var_idx, 'Value'].iloc[0] <= 1
    
    # RMSE and MAE should be positive
    rmse_idx = result['Metric'] == 'RMSE'
    mae_idx = result['Metric'] == 'MAE'
    
    assert result.loc[rmse_idx, 'Value'].iloc[0] > 0
    assert result.loc[mae_idx, 'Value'].iloc[0] > 0

def test_different_input_types(test_data):
    """Test if function works with different input types"""
    # Test with numpy arrays
    X_numpy = test_data['X'].to_numpy()
    y_numpy = test_data['y'].to_numpy()
    
    result_numpy = evaluate_model_with_cross_validation(
        model=test_data['model'],
        X=X_numpy,
        y=y_numpy,
        cv=5,
        target_range=test_data['target_range']
    )
    
    assert isinstance(result_numpy, pd.DataFrame)
    
    # Test with pandas objects
    result_pandas = evaluate_model_with_cross_validation(
        model=test_data['model'],
        X=test_data['X'],
        y=test_data['y'],
        cv=5,
        target_range=test_data['target_range']
    )
    
    assert isinstance(result_pandas, pd.DataFrame)

def test_target_range_calculation(test_data):
    """Test if target_range is correctly calculated when not provided"""
    result = evaluate_model_with_cross_validation(
        model=test_data['model'],
        X=test_data['X'],
        y=test_data['y'],
        cv=5
    )
    
    # Check if function runs without target_range
    assert isinstance(result, pd.DataFrame)
    
    # Verify calculations use correct target range
    expected_range = np.max(test_data['y']) - np.min(test_data['y'])
    rmse_idx = result['Metric'] == 'RMSE'
    calculation = result.loc[rmse_idx, 'Calculation'].iloc[0]
    
    assert f'{expected_range:.2f}' in calculation 