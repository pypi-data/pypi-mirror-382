import pytest
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.datasets import make_regression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from extended_sklearn_metrics import (
    calculate_residual_diagnostics,
    create_residual_summary_report,
    print_residual_diagnostics_report
)


class TestResidualDiagnostics:
    """Test suite for residual diagnostics functionality"""
    
    @pytest.fixture
    def simple_regression_data(self):
        """Create simple regression test data"""
        X, y = make_regression(
            n_samples=100,
            n_features=3,
            noise=0.5,
            random_state=42
        )
        return {
            'X': pd.DataFrame(X, columns=[f'feature_{i}' for i in range(3)]),
            'y': pd.Series(y),
            'model': LinearRegression()
        }
    
    @pytest.fixture  
    def noisy_regression_data(self):
        """Create regression data with more noise for testing edge cases"""
        X, y = make_regression(
            n_samples=150,
            n_features=5,
            noise=2.0,
            random_state=123
        )
        return {
            'X': pd.DataFrame(X, columns=[f'feature_{i}' for i in range(5)]),
            'y': pd.Series(y),
            'model': LinearRegression()
        }
    
    def test_basic_residual_diagnostics(self, simple_regression_data):
        """Test basic residual diagnostics calculation"""
        diagnostics = calculate_residual_diagnostics(
            model=simple_regression_data['model'],
            X=simple_regression_data['X'],
            y=simple_regression_data['y'],
            cv=3
        )
        
        # Check that all required components are present
        required_keys = [
            'residuals', 'predictions', 'true_values',
            'residual_statistics', 'sample_size'
        ]
        
        for key in required_keys:
            assert key in diagnostics
        
        # Check data types and shapes
        assert isinstance(diagnostics['residuals'], np.ndarray)
        assert isinstance(diagnostics['predictions'], np.ndarray)
        assert isinstance(diagnostics['true_values'], np.ndarray)
        assert len(diagnostics['residuals']) == 100
        assert len(diagnostics['predictions']) == 100
        assert len(diagnostics['true_values']) == 100
        assert diagnostics['sample_size'] == 100
    
    def test_residual_statistics(self, simple_regression_data):
        """Test residual statistics calculations"""
        diagnostics = calculate_residual_diagnostics(
            model=simple_regression_data['model'],
            X=simple_regression_data['X'],
            y=simple_regression_data['y'],
            cv=3
        )
        
        stats = diagnostics['residual_statistics']
        residuals = diagnostics['residuals']
        
        # Check basic statistics
        assert 'mean' in stats
        assert 'std' in stats
        assert 'min' in stats
        assert 'max' in stats
        assert 'median' in stats
        assert 'q25' in stats
        assert 'q75' in stats
        assert 'iqr' in stats
        
        # Verify calculations
        np.testing.assert_almost_equal(stats['mean'], np.mean(residuals))
        np.testing.assert_almost_equal(stats['std'], np.std(residuals, ddof=1))
        np.testing.assert_almost_equal(stats['min'], np.min(residuals))
        np.testing.assert_almost_equal(stats['max'], np.max(residuals))
        np.testing.assert_almost_equal(stats['median'], np.median(residuals))
        np.testing.assert_almost_equal(stats['iqr'], np.percentile(residuals, 75) - np.percentile(residuals, 25))
    
    def test_normality_tests(self, simple_regression_data):
        """Test normality tests in diagnostics"""
        diagnostics = calculate_residual_diagnostics(
            model=simple_regression_data['model'],
            X=simple_regression_data['X'],
            y=simple_regression_data['y'],
            cv=3
        )
        
        if 'normality_tests' in diagnostics:
            norm_tests = diagnostics['normality_tests']
            
            # Check Shapiro-Wilk test (if available)
            if 'shapiro_wilk' in norm_tests:
                sw = norm_tests['shapiro_wilk']
                assert 'statistic' in sw
                assert 'p_value' in sw
                assert 'is_normal' in sw
                assert isinstance(sw['is_normal'], bool)
                assert 0 <= sw['p_value'] <= 1
            
            # Check Kolmogorov-Smirnov test
            if 'kolmogorov_smirnov' in norm_tests:
                ks = norm_tests['kolmogorov_smirnov']
                assert 'statistic' in ks
                assert 'p_value' in ks
                assert 'is_normal' in ks
                assert isinstance(ks['is_normal'], bool)
            
            # Check Anderson-Darling test
            if 'anderson_darling' in norm_tests:
                ad = norm_tests['anderson_darling']
                assert 'statistic' in ad
                assert 'critical_value_5pct' in ad
                assert 'is_normal' in ad
                assert isinstance(ad['is_normal'], bool)
    
    def test_heteroscedasticity_tests(self, simple_regression_data):
        """Test heteroscedasticity tests"""
        diagnostics = calculate_residual_diagnostics(
            model=simple_regression_data['model'],
            X=simple_regression_data['X'],
            y=simple_regression_data['y'],
            cv=3
        )
        
        if 'heteroscedasticity_tests' in diagnostics:
            hetero_tests = diagnostics['heteroscedasticity_tests']
            
            # Check Breusch-Pagan test
            if 'breusch_pagan_simple' in hetero_tests:
                bp = hetero_tests['breusch_pagan_simple']
                assert 'correlation' in bp
                assert 'is_homoscedastic' in bp
                assert isinstance(bp['is_homoscedastic'], bool)
                assert -1 <= bp['correlation'] <= 1
            
            # Check Goldfeld-Quandt test
            if 'goldfeld_quandt' in hetero_tests:
                gq = hetero_tests['goldfeld_quandt']
                assert 'f_statistic' in gq
                assert 'is_homoscedastic' in gq
                assert isinstance(gq['is_homoscedastic'], bool)
                assert gq['f_statistic'] >= 1.0  # F-statistic should be >= 1
    
    def test_autocorrelation_tests(self, simple_regression_data):
        """Test autocorrelation tests"""
        diagnostics = calculate_residual_diagnostics(
            model=simple_regression_data['model'],
            X=simple_regression_data['X'],
            y=simple_regression_data['y'],
            cv=3
        )
        
        if 'autocorrelation_tests' in diagnostics:
            autocorr_tests = diagnostics['autocorrelation_tests']
            
            if 'durbin_watson' in autocorr_tests:
                dw = autocorr_tests['durbin_watson']
                assert 'statistic' in dw
                assert 'interpretation' in dw
                assert 0 <= dw['statistic'] <= 4  # Durbin-Watson range
                assert isinstance(dw['interpretation'], str)
    
    def test_outlier_analysis(self, simple_regression_data):
        """Test outlier analysis"""
        diagnostics = calculate_residual_diagnostics(
            model=simple_regression_data['model'],
            X=simple_regression_data['X'],
            y=simple_regression_data['y'],
            cv=3
        )
        
        if 'outlier_analysis' in diagnostics:
            outliers = diagnostics['outlier_analysis']
            
            required_keys = [
                'standardized_residuals', 'outliers_2std', 'outliers_3std',
                'outlier_indices_2std', 'outlier_indices_3std', 'max_abs_std_residual'
            ]
            
            for key in required_keys:
                assert key in outliers
            
            # Check data types
            assert isinstance(outliers['outliers_2std'], (int, np.integer))
            assert isinstance(outliers['outliers_3std'], (int, np.integer))
            assert isinstance(outliers['outlier_indices_2std'], list)
            assert isinstance(outliers['outlier_indices_3std'], list)
            
            # Logical checks
            assert outliers['outliers_3std'] <= outliers['outliers_2std']  # 3σ subset of 2σ
            assert len(outliers['outlier_indices_3std']) == outliers['outliers_3std']
            assert len(outliers['outlier_indices_2std']) == outliers['outliers_2std']
    
    def test_create_residual_summary_report(self, simple_regression_data):
        """Test creation of residual summary report DataFrame"""
        diagnostics = calculate_residual_diagnostics(
            model=simple_regression_data['model'],
            X=simple_regression_data['X'],
            y=simple_regression_data['y'],
            cv=3
        )
        
        summary_df = create_residual_summary_report(diagnostics)
        
        # Check DataFrame structure
        assert isinstance(summary_df, pd.DataFrame)
        expected_columns = ['Category', 'Test/Statistic', 'Value', 'Interpretation']
        assert list(summary_df.columns) == expected_columns
        
        # Check that we have some basic categories
        categories = summary_df['Category'].unique()
        assert 'Residual Statistics' in categories
        
        # Check that basic statistics are present
        residual_stats = summary_df[summary_df['Category'] == 'Residual Statistics']
        stat_names = residual_stats['Test/Statistic'].tolist()
        
        basic_stats = ['Mean', 'Std Dev', 'Min', 'Max', 'Median', 'IQR']
        for stat in basic_stats:
            assert stat in stat_names
    
    def test_print_residual_diagnostics_report(self, simple_regression_data, capsys):
        """Test printing of residual diagnostics report"""
        diagnostics = calculate_residual_diagnostics(
            model=simple_regression_data['model'],
            X=simple_regression_data['X'],
            y=simple_regression_data['y'],
            cv=3
        )
        
        # This should not raise an error
        print_residual_diagnostics_report(diagnostics)
        
        # Check that something was printed
        captured = capsys.readouterr()
        assert "RESIDUAL DIAGNOSTICS REPORT" in captured.out
        assert "OVERALL ASSESSMENT:" in captured.out
        assert "DETAILED DIAGNOSTICS:" in captured.out
        assert "RECOMMENDATIONS:" in captured.out
    
    def test_different_cv_values(self, simple_regression_data):
        """Test diagnostics with different CV values"""
        for cv in [3, 5, 10]:
            diagnostics = calculate_residual_diagnostics(
                model=simple_regression_data['model'],
                X=simple_regression_data['X'],
                y=simple_regression_data['y'],
                cv=cv
            )
            
            assert diagnostics['sample_size'] == 100
            assert len(diagnostics['residuals']) == 100
    
    def test_pipeline_compatibility(self, simple_regression_data):
        """Test that residual diagnostics work with pipelines"""
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('regressor', LinearRegression())
        ])
        
        diagnostics = calculate_residual_diagnostics(
            model=pipeline,
            X=simple_regression_data['X'],
            y=simple_regression_data['y'],
            cv=3
        )
        
        # Should work without error and return valid diagnostics
        assert 'residuals' in diagnostics
        assert 'residual_statistics' in diagnostics
        assert diagnostics['sample_size'] == 100
    
    def test_small_sample_handling(self):
        """Test handling of small samples"""
        # Create very small dataset
        X = np.random.randn(15, 2)
        y = X[:, 0] + X[:, 1] + np.random.randn(15) * 0.1
        model = LinearRegression()
        
        diagnostics = calculate_residual_diagnostics(
            model=model,
            X=X,
            y=y,
            cv=3
        )
        
        assert diagnostics['sample_size'] == 15
        assert 'residual_statistics' in diagnostics
    
    def test_perfect_model_case(self):
        """Test diagnostics with a perfect model (no noise)"""
        # Create perfect linear relationship
        X = np.random.randn(50, 2)
        y = 2 * X[:, 0] + 3 * X[:, 1]  # No noise
        model = LinearRegression()
        
        diagnostics = calculate_residual_diagnostics(
            model=model,
            X=X,
            y=y,
            cv=3
        )
        
        # Residuals should be very small (numerical precision)
        residuals = diagnostics['residuals']
        assert np.mean(np.abs(residuals)) < 1e-10  # Very small residuals
    
    def test_high_noise_case(self, noisy_regression_data):
        """Test diagnostics with high noise data"""
        diagnostics = calculate_residual_diagnostics(
            model=noisy_regression_data['model'],
            X=noisy_regression_data['X'],
            y=noisy_regression_data['y'],
            cv=3
        )
        
        # Should handle noisy data without errors
        assert 'residuals' in diagnostics
        stats = diagnostics['residual_statistics']
        
        # With high noise, std should be relatively large
        assert stats['std'] > 0.5  # Adjust threshold as needed
    
    def test_edge_cases_validation(self, simple_regression_data):
        """Test various edge cases and input validation"""
        # Test with cv too large
        with pytest.raises(ValueError):
            calculate_residual_diagnostics(
                model=simple_regression_data['model'],
                X=simple_regression_data['X'][:5],  # Only 5 samples
                y=simple_regression_data['y'][:5],
                cv=10  # Too many folds
            )