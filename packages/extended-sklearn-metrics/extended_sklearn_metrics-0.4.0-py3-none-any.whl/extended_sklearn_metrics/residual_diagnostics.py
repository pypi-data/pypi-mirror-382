"""
Residual diagnostics and analysis for regression models
"""
import numpy as np
import pandas as pd
from sklearn.model_selection import cross_val_predict
from typing import Union, Optional, Tuple, Dict, Any
import warnings
from scipy import stats


def calculate_residual_diagnostics(
    model,
    X: Union[pd.DataFrame, np.ndarray],
    y: Union[pd.Series, np.ndarray],
    cv: int = 5
) -> Dict[str, Any]:
    """
    Calculate comprehensive residual diagnostics for regression models.
    
    Parameters
    ----------
    model : estimator object
        The fitted regression model
    X : array-like of shape (n_samples, n_features)
        Feature data
    y : array-like of shape (n_samples,)
        Target values
    cv : int, default=5
        Number of cross-validation folds for predictions
        
    Returns
    -------
    dict
        Dictionary containing residual analysis results
    """
    # Get cross-validated predictions
    y_pred = cross_val_predict(model, X, y, cv=cv)
    
    # Convert to numpy arrays for calculations
    y_true = np.asarray(y)
    residuals = y_true - y_pred
    
    # Basic residual statistics
    residual_stats = {
        'mean': np.mean(residuals),
        'std': np.std(residuals, ddof=1),
        'min': np.min(residuals),
        'max': np.max(residuals),
        'median': np.median(residuals),
        'q25': np.percentile(residuals, 25),
        'q75': np.percentile(residuals, 75),
        'iqr': np.percentile(residuals, 75) - np.percentile(residuals, 25)
    }
    
    # Normality tests
    normality_tests = {}
    try:
        # Shapiro-Wilk test (good for small samples)
        if len(residuals) <= 5000:  # Shapiro-Wilk limit
            shapiro_stat, shapiro_p = stats.shapiro(residuals)
            normality_tests['shapiro_wilk'] = {
                'statistic': shapiro_stat,
                'p_value': shapiro_p,
                'is_normal': bool(shapiro_p > 0.05)
            }
        
        # Kolmogorov-Smirnov test
        ks_stat, ks_p = stats.kstest(residuals, 'norm', 
                                    args=(np.mean(residuals), np.std(residuals, ddof=1)))
        normality_tests['kolmogorov_smirnov'] = {
            'statistic': ks_stat,
            'p_value': ks_p,
            'is_normal': bool(ks_p > 0.05)
        }
        
        # Anderson-Darling test
        ad_stat, ad_critical_vals, ad_significance_levels = stats.anderson(residuals, dist='norm')
        # Use 5% significance level (index 2: [15%, 10%, 5%, 2.5%, 1%])
        normality_tests['anderson_darling'] = {
            'statistic': ad_stat,
            'critical_value_5pct': ad_critical_vals[2],
            'is_normal': bool(ad_stat < ad_critical_vals[2])
        }
        
    except Exception as e:
        warnings.warn(f"Some normality tests failed: {e}", UserWarning)
    
    # Heteroscedasticity tests
    heteroscedasticity_tests = {}
    try:
        # Breusch-Pagan test (simplified version)
        # Regress squared residuals on predictions
        residuals_squared = residuals ** 2
        
        # Calculate correlation between squared residuals and predictions
        bp_correlation = np.corrcoef(residuals_squared, y_pred)[0, 1]
        
        # Simplified test: strong correlation suggests heteroscedasticity
        heteroscedasticity_tests['breusch_pagan_simple'] = {
            'correlation': bp_correlation,
            'is_homoscedastic': bool(abs(bp_correlation) < 0.3)  # Simple threshold
        }
        
        # Goldfeld-Quandt test (split sample)
        n = len(residuals)
        if n > 30:  # Minimum sample size
            # Sort by predictions and split into two groups
            sorted_indices = np.argsort(y_pred)
            n_split = n // 3
            
            # First and last thirds
            group1_residuals = residuals_squared[sorted_indices[:n_split]]
            group2_residuals = residuals_squared[sorted_indices[-n_split:]]
            
            # F-test for equal variances
            var1 = np.var(group1_residuals, ddof=1)
            var2 = np.var(group2_residuals, ddof=1)
            
            f_stat = max(var1, var2) / min(var1, var2)
            # Simplified: assume homoscedastic if F-stat < 2
            heteroscedasticity_tests['goldfeld_quandt'] = {
                'f_statistic': f_stat,
                'is_homoscedastic': bool(f_stat < 2.0)
            }
            
    except Exception as e:
        warnings.warn(f"Heteroscedasticity tests failed: {e}", UserWarning)
    
    # Autocorrelation test (Durbin-Watson)
    autocorrelation_tests = {}
    try:
        # Durbin-Watson statistic
        diff_residuals = np.diff(residuals)
        dw_stat = np.sum(diff_residuals**2) / np.sum(residuals**2)
        
        autocorrelation_tests['durbin_watson'] = {
            'statistic': dw_stat,
            'interpretation': _interpret_durbin_watson(dw_stat)
        }
        
    except Exception as e:
        warnings.warn(f"Autocorrelation test failed: {e}", UserWarning)
    
    # Outlier detection
    outlier_analysis = {}
    try:
        # Standardized residuals
        std_residuals = residuals / np.std(residuals, ddof=1)
        
        # Various outlier thresholds
        outlier_analysis = {
            'standardized_residuals': std_residuals,
            'outliers_2std': np.sum(np.abs(std_residuals) > 2),
            'outliers_3std': np.sum(np.abs(std_residuals) > 3),
            'outlier_indices_2std': np.where(np.abs(std_residuals) > 2)[0].tolist(),
            'outlier_indices_3std': np.where(np.abs(std_residuals) > 3)[0].tolist(),
            'max_abs_std_residual': np.max(np.abs(std_residuals))
        }
        
    except Exception as e:
        warnings.warn(f"Outlier analysis failed: {e}", UserWarning)
    
    # Compile all results
    diagnostics = {
        'residuals': residuals,
        'predictions': y_pred,
        'true_values': y_true,
        'residual_statistics': residual_stats,
        'normality_tests': normality_tests,
        'heteroscedasticity_tests': heteroscedasticity_tests,
        'autocorrelation_tests': autocorrelation_tests,
        'outlier_analysis': outlier_analysis,
        'sample_size': len(residuals)
    }
    
    return diagnostics


def _interpret_durbin_watson(dw_stat: float) -> str:
    """Interpret Durbin-Watson statistic"""
    if dw_stat < 1.5:
        return "Positive autocorrelation likely"
    elif dw_stat > 2.5:
        return "Negative autocorrelation likely"
    else:
        return "No strong autocorrelation"


def create_residual_summary_report(diagnostics: Dict[str, Any]) -> pd.DataFrame:
    """
    Create a summary report DataFrame from residual diagnostics.
    
    Parameters
    ----------
    diagnostics : dict
        Results from calculate_residual_diagnostics
        
    Returns
    -------
    pd.DataFrame
        Summary report of residual diagnostics
    """
    stats = diagnostics['residual_statistics']
    
    # Basic statistics section
    summary_data = []
    
    # Residual statistics
    summary_data.extend([
        ['Residual Statistics', 'Mean', f"{stats['mean']:.6f}", 'Should be close to 0'],
        ['Residual Statistics', 'Std Dev', f"{stats['std']:.4f}", 'Measure of residual spread'],
        ['Residual Statistics', 'Min', f"{stats['min']:.4f}", 'Most negative residual'],
        ['Residual Statistics', 'Max', f"{stats['max']:.4f}", 'Most positive residual'],
        ['Residual Statistics', 'Median', f"{stats['median']:.6f}", 'Should be close to 0'],
        ['Residual Statistics', 'IQR', f"{stats['iqr']:.4f}", 'Interquartile range']
    ])
    
    # Normality tests
    if 'normality_tests' in diagnostics:
        norm_tests = diagnostics['normality_tests']
        
        if 'shapiro_wilk' in norm_tests:
            sw = norm_tests['shapiro_wilk']
            result = '✅ Normal' if sw['is_normal'] else '❌ Not Normal'
            summary_data.append([
                'Normality Tests', 'Shapiro-Wilk', f"p={sw['p_value']:.4f} ({result})", 
                'p > 0.05 indicates normality'
            ])
        
        if 'kolmogorov_smirnov' in norm_tests:
            ks = norm_tests['kolmogorov_smirnov']
            result = '✅ Normal' if ks['is_normal'] else '❌ Not Normal'
            summary_data.append([
                'Normality Tests', 'Kolmogorov-Smirnov', f"p={ks['p_value']:.4f} ({result})",
                'p > 0.05 indicates normality'
            ])
        
        if 'anderson_darling' in norm_tests:
            ad = norm_tests['anderson_darling']
            result = '✅ Normal' if ad['is_normal'] else '❌ Not Normal'
            summary_data.append([
                'Normality Tests', 'Anderson-Darling', f"stat={ad['statistic']:.4f} ({result})",
                'Statistic < critical value indicates normality'
            ])
    
    # Heteroscedasticity tests
    if 'heteroscedasticity_tests' in diagnostics:
        hetero_tests = diagnostics['heteroscedasticity_tests']
        
        if 'breusch_pagan_simple' in hetero_tests:
            bp = hetero_tests['breusch_pagan_simple']
            result = '✅ Homoscedastic' if bp['is_homoscedastic'] else '❌ Heteroscedastic'
            summary_data.append([
                'Heteroscedasticity Tests', 'Breusch-Pagan (Simple)', f"corr={bp['correlation']:.4f} ({result})",
                'Low correlation indicates homoscedasticity'
            ])
        
        if 'goldfeld_quandt' in hetero_tests:
            gq = hetero_tests['goldfeld_quandt']
            result = '✅ Homoscedastic' if gq['is_homoscedastic'] else '❌ Heteroscedastic'
            summary_data.append([
                'Heteroscedasticity Tests', 'Goldfeld-Quandt', f"F={gq['f_statistic']:.4f} ({result})",
                'F < 2.0 suggests homoscedasticity'
            ])
    
    # Autocorrelation tests
    if 'autocorrelation_tests' in diagnostics:
        autocorr_tests = diagnostics['autocorrelation_tests']
        
        if 'durbin_watson' in autocorr_tests:
            dw = autocorr_tests['durbin_watson']
            summary_data.append([
                'Autocorrelation Tests', 'Durbin-Watson', f"{dw['statistic']:.4f} ({dw['interpretation']})",
                'Values near 2.0 indicate no autocorrelation'
            ])
    
    # Outlier analysis
    if 'outlier_analysis' in diagnostics:
        outliers = diagnostics['outlier_analysis']
        
        total_obs = diagnostics['sample_size']
        pct_2std = (outliers['outliers_2std'] / total_obs) * 100
        pct_3std = (outliers['outliers_3std'] / total_obs) * 100
        
        summary_data.extend([
            ['Outlier Analysis', 'Outliers (>2σ)', f"{outliers['outliers_2std']} ({pct_2std:.1f}%)", 
             'Expected ~5% in normal distribution'],
            ['Outlier Analysis', 'Outliers (>3σ)', f"{outliers['outliers_3std']} ({pct_3std:.1f}%)", 
             'Expected ~0.3% in normal distribution'],
            ['Outlier Analysis', 'Max |Std Residual|', f"{outliers['max_abs_std_residual']:.4f}", 
             'Values >3 are concerning']
        ])
    
    # Create DataFrame
    df = pd.DataFrame(summary_data, columns=['Category', 'Test/Statistic', 'Value', 'Interpretation'])
    
    return df


def print_residual_diagnostics_report(diagnostics: Dict[str, Any]) -> None:
    """
    Print a comprehensive residual diagnostics report.
    
    Parameters
    ----------
    diagnostics : dict
        Results from calculate_residual_diagnostics
    """
    print("=" * 80)
    print("RESIDUAL DIAGNOSTICS REPORT")
    print("=" * 80)
    
    stats = diagnostics['residual_statistics']
    
    print(f"Sample Size: {diagnostics['sample_size']}")
    print()
    
    # Overall assessment
    issues = []
    
    # Check mean close to zero
    if abs(stats['mean']) > 0.1 * stats['std']:
        issues.append("⚠️  Residual mean not close to zero")
    
    # Check normality
    if 'normality_tests' in diagnostics:
        norm_tests = diagnostics['normality_tests']
        normal_count = sum(1 for test in norm_tests.values() 
                          if isinstance(test, dict) and test.get('is_normal', False))
        total_norm_tests = len([t for t in norm_tests.values() if isinstance(t, dict)])
        
        if total_norm_tests > 0 and normal_count / total_norm_tests < 0.5:
            issues.append("⚠️  Residuals may not be normally distributed")
    
    # Check homoscedasticity
    if 'heteroscedasticity_tests' in diagnostics:
        hetero_tests = diagnostics['heteroscedasticity_tests']
        homo_count = sum(1 for test in hetero_tests.values() 
                        if isinstance(test, dict) and test.get('is_homoscedastic', False))
        total_hetero_tests = len([t for t in hetero_tests.values() if isinstance(t, dict)])
        
        if total_hetero_tests > 0 and homo_count / total_hetero_tests < 0.5:
            issues.append("⚠️  Possible heteroscedasticity detected")
    
    # Check outliers
    if 'outlier_analysis' in diagnostics:
        outliers = diagnostics['outlier_analysis']
        total_obs = diagnostics['sample_size']
        
        if outliers['outliers_3std'] > 0:
            pct = (outliers['outliers_3std'] / total_obs) * 100
            if pct > 1.0:  # More than 1% are extreme outliers
                issues.append(f"⚠️  {outliers['outliers_3std']} extreme outliers detected ({pct:.1f}%)")
    
    # Overall assessment
    print("OVERALL ASSESSMENT:")
    print("-" * 20)
    if not issues:
        print("✅ No major issues detected in residual analysis")
        print("   The model appears to meet regression assumptions reasonably well.")
    else:
        print("❌ Issues detected:")
        for issue in issues:
            print(f"   {issue}")
    
    print()
    
    # Detailed summary
    summary_df = create_residual_summary_report(diagnostics)
    print("DETAILED DIAGNOSTICS:")
    print("-" * 20)
    
    # Group by category for better readability
    for category in summary_df['Category'].unique():
        print(f"\n{category}:")
        category_data = summary_df[summary_df['Category'] == category]
        for _, row in category_data.iterrows():
            print(f"  {row['Test/Statistic']:20}: {row['Value']:25} | {row['Interpretation']}")
    
    print()
    
    # Recommendations
    print("RECOMMENDATIONS:")
    print("-" * 15)
    
    if not issues:
        print("✅ Model residuals look good! Consider:")
        print("   • Model is likely well-specified")
        print("   • Predictions should be reliable")
        print("   • Consider validating on additional data")
    else:
        print("💡 Consider these improvements:")
        
        if any("mean not close to zero" in issue for issue in issues):
            print("   • Check for systematic bias - missing features or wrong model form")
        
        if any("not be normally distributed" in issue for issue in issues):
            print("   • Try data transformations (log, sqrt, Box-Cox)")
            print("   • Consider robust regression methods")
        
        if any("heteroscedasticity" in issue for issue in issues):
            print("   • Use weighted least squares or robust standard errors")
            print("   • Try feature transformations or polynomial terms")
        
        if any("outliers" in issue for issue in issues):
            print("   • Investigate outliers - data errors or interesting cases?")
            print("   • Consider robust regression methods")
    
    print("=" * 80)