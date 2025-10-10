"""
Comprehensive evaluation reporting and visualization functions.
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List
import warnings


def create_evaluation_report(evaluation_results: Dict[str, Any]) -> pd.DataFrame:
    """
    Create a comprehensive evaluation report DataFrame.
    
    Parameters
    ----------
    evaluation_results : dict
        Results from final_model_evaluation function
        
    Returns
    -------
    pd.DataFrame
        Comprehensive evaluation report
    """
    report_data = []
    
    # Basic Information
    report_data.extend([
        ['Model Info', 'Task Type', evaluation_results['task_type'], 
         'Type of machine learning task'],
        ['Model Info', 'Training Samples', str(evaluation_results['train_size']),
         'Number of training samples'],
        ['Model Info', 'Test Samples', str(evaluation_results['test_size']),
         'Number of test samples'],
        ['Model Info', 'Features', str(evaluation_results['n_features']),
         'Number of input features']
    ])
    
    # Performance Metrics
    if 'performance' in evaluation_results:
        perf = evaluation_results['performance']
        for metric, value in perf.items():
            if isinstance(value, (int, float)):
                report_data.append([
                    'Performance', metric.replace('_', ' ').title(), 
                    f'{value:.4f}', f'Test set {metric}'
                ])
            elif isinstance(value, dict) and metric == 'class_distribution':
                for class_label, count in value.items():
                    report_data.append([
                        'Class Distribution', f'Class {class_label}', str(count),
                        'Number of samples in test set'
                    ])
    
    # CV Stability
    if 'cv_stability' in evaluation_results:
        cv_results = evaluation_results['cv_stability']
        for metric, stats in cv_results.items():
            if isinstance(stats, dict):
                report_data.extend([
                    ['CV Stability', f'{metric.title()} Mean', f"{stats['mean']:.4f}",
                     'Cross-validation mean score'],
                    ['CV Stability', f'{metric.title()} Std', f"{stats['std']:.4f}",
                     'Cross-validation standard deviation'],
                    ['CV Stability', f'{metric.title()} CV', f"{stats['cv']:.4f}",
                     'Coefficient of variation (std/mean)']
                ])
    
    # Feature Importance Summary
    if 'feature_importance' in evaluation_results:
        fi = evaluation_results['feature_importance']
        
        # Get top features from each importance method
        for importance_type, importance_data in fi.items():
            if isinstance(importance_data, dict) and 'values' in importance_data:
                values = importance_data['values']
                features = importance_data['features']
                
                # Get top 3 features
                if importance_type == 'builtin_importance':
                    top_indices = np.argsort(values)[-3:][::-1]
                    for i, idx in enumerate(top_indices):
                        report_data.append([
                            'Feature Importance', f'Top {i+1} (Built-in)', 
                            f"{features[idx]} ({values[idx]:.4f})",
                            'Built-in feature importance'
                        ])
                        
                elif importance_type == 'permutation_importance':
                    importances = importance_data.get('importances_mean', [])
                    if importances:
                        top_indices = np.argsort(importances)[-3:][::-1]
                        for i, idx in enumerate(top_indices):
                            report_data.append([
                                'Feature Importance', f'Top {i+1} (Permutation)', 
                                f"{features[idx]} ({importances[idx]:.4f})",
                                'Permutation feature importance'
                            ])
    
    # Error Analysis Summary
    if 'error_analysis' in evaluation_results:
        error = evaluation_results['error_analysis']
        
        if evaluation_results['task_type'] == 'classification':
            if 'misclassification_rate' in error:
                report_data.append([
                    'Error Analysis', 'Misclassification Rate', 
                    f"{error['misclassification_rate']:.4f}",
                    'Proportion of misclassified samples'
                ])
        else:
            for metric in ['residuals_mean', 'residuals_std', 'abs_residuals_mean']:
                if metric in error:
                    report_data.append([
                        'Error Analysis', metric.replace('_', ' ').title(),
                        f"{error[metric]:.4f}",
                        f'Residual analysis: {metric}'
                    ])
    
    # Fairness Analysis Summary
    if 'fairness_analysis' in evaluation_results:
        fairness = evaluation_results['fairness_analysis']
        
        for attr_name, attr_results in fairness.items():
            if 'disparities' in attr_results:
                disparities = attr_results['disparities']
                for disparity_metric, disparity_value in disparities.items():
                    if 'ratio' in disparity_metric:
                        report_data.append([
                            'Fairness Analysis', 
                            f'{attr_name} - {disparity_metric.replace("_", " ").title()}',
                            f"{disparity_value:.4f}",
                            f'Fairness disparity ratio for {attr_name}'
                        ])
    
    # Model Interpretation Summary
    if 'interpretation' in evaluation_results:
        interp = evaluation_results['interpretation']
        
        if 'model_complexity' in interp:
            complexity = interp['model_complexity']
            for metric, value in complexity.items():
                if isinstance(value, (int, float)):
                    report_data.append([
                        'Model Complexity', metric.replace('_', ' ').title(),
                        str(value), f'Model complexity: {metric}'
                    ])
    
    # Create DataFrame
    df = pd.DataFrame(report_data, columns=['Category', 'Metric', 'Value', 'Description'])
    return df


def print_evaluation_summary(evaluation_results: Dict[str, Any]) -> None:
    """
    Print a comprehensive evaluation summary.
    
    Parameters
    ----------
    evaluation_results : dict
        Results from final_model_evaluation function
    """
    # Type check to ensure we have the right input
    if not isinstance(evaluation_results, dict):
        raise TypeError(
            f"Expected dictionary from final_model_evaluation(), "
            f"but got {type(evaluation_results)}. "
            f"Make sure you're passing the result of final_model_evaluation(), "
            f"not create_evaluation_report()."
        )
    
    # Check for required keys
    required_keys = ['task_type', 'train_size', 'test_size', 'n_features']
    missing_keys = [key for key in required_keys if key not in evaluation_results]
    if missing_keys:
        raise KeyError(
            f"Missing required keys in evaluation_results: {missing_keys}. "
            f"Make sure you're passing the result of final_model_evaluation()."
        )
    
    print("=" * 80)
    print("COMPREHENSIVE MODEL EVALUATION REPORT")
    print("=" * 80)
    
    # Basic Info
    print(f"Task Type: {evaluation_results['task_type'].title()}")
    print(f"Training Samples: {evaluation_results['train_size']:,}")
    print(f"Test Samples: {evaluation_results['test_size']:,}")
    print(f"Features: {evaluation_results['n_features']:,}")
    print()
    
    # Performance Summary
    if 'performance' in evaluation_results:
        print("PERFORMANCE ON TEST SET:")
        print("-" * 25)
        perf = evaluation_results['performance']
        
        if evaluation_results['task_type'] == 'classification':
            key_metrics = ['accuracy', 'f1_weighted', 'precision_weighted', 'recall_weighted']
            if 'roc_auc' in perf:
                key_metrics.append('roc_auc')
        else:
            key_metrics = ['r2', 'rmse', 'mae']
        
        for metric in key_metrics:
            if metric in perf:
                print(f"  {metric.replace('_', ' ').title():20}: {perf[metric]:.4f}")
        print()
    
    # Model Stability
    if 'cv_stability' in evaluation_results:
        print("MODEL STABILITY (Cross-Validation):")
        print("-" * 35)
        cv_results = evaluation_results['cv_stability']
        
        for metric, stats in list(cv_results.items())[:3]:  # Show top 3 metrics
            if isinstance(stats, dict):
                print(f"  {metric.title():20}: {stats['mean']:.4f} ± {stats['std']:.4f}")
        print()
    
    # Feature Importance
    if 'feature_importance' in evaluation_results:
        fi = evaluation_results['feature_importance']
        print("TOP IMPORTANT FEATURES:")
        print("-" * 25)
        
        # Show permutation importance if available, otherwise built-in
        if 'permutation_importance' in fi:
            importances = fi['permutation_importance']['importances_mean']
            features = fi['permutation_importance']['features']
            method = "Permutation"
        elif 'builtin_importance' in fi:
            importances = fi['builtin_importance']['values']
            features = fi['builtin_importance']['features']
            method = "Built-in"
        else:
            importances = None
        
        if importances:
            top_indices = np.argsort(importances)[-5:][::-1]  # Top 5
            for i, idx in enumerate(top_indices):
                print(f"  {i+1:2}. {features[idx]:25}: {importances[idx]:.4f}")
            print(f"     (Using {method} importance)")
            print()
    
    # Error Analysis Summary
    if 'error_analysis' in evaluation_results:
        error = evaluation_results['error_analysis']
        print("ERROR ANALYSIS:")
        print("-" * 15)
        
        if evaluation_results['task_type'] == 'classification':
            if 'misclassification_rate' in error:
                print(f"  Misclassification Rate: {error['misclassification_rate']:.4f}")
            if 'n_misclassified' in error:
                print(f"  Misclassified Samples: {error['n_misclassified']}")
        else:
            key_error_metrics = ['residuals_mean', 'residuals_std', 'abs_residuals_mean']
            for metric in key_error_metrics:
                if metric in error:
                    print(f"  {metric.replace('_', ' ').title():20}: {error[metric]:.4f}")
        print()
    
    # Fairness Analysis
    if 'fairness_analysis' in evaluation_results:
        fairness = evaluation_results['fairness_analysis']
        print("FAIRNESS ANALYSIS:")
        print("-" * 18)
        
        for attr_name, attr_results in fairness.items():
            print(f"  Protected Attribute: {attr_name}")
            
            if 'group_metrics' in attr_results:
                group_metrics = attr_results['group_metrics']
                print("  Group Performance:")
                
                for group, metrics in group_metrics.items():
                    if evaluation_results['task_type'] == 'classification':
                        key_metric = metrics.get('accuracy', metrics.get('f1', 0))
                        print(f"    {group:10}: {key_metric:.4f} (n={metrics.get('size', 0)})")
                    else:
                        key_metric = metrics.get('r2', metrics.get('mae', 0))
                        print(f"    {group:10}: {key_metric:.4f} (n={metrics.get('size', 0)})")
            
            if 'disparities' in attr_results:
                disparities = attr_results['disparities']
                max_disparity = 0
                for disp_name, disp_value in disparities.items():
                    if 'ratio' in disp_name:
                        max_disparity = max(max_disparity, disp_value)
                
                print(f"  Max Disparity Ratio: {max_disparity:.3f}")
                
                if max_disparity > 1.2:
                    print("  ⚠️  Potential fairness concern detected")
                else:
                    print("  ✅ Fairness metrics look reasonable")
            print()
    
    # Overall Assessment
    print("OVERALL ASSESSMENT:")
    print("-" * 20)
    
    # Performance assessment
    if 'performance' in evaluation_results:
        perf = evaluation_results['performance']
        
        if evaluation_results['task_type'] == 'classification':
            key_score = perf.get('accuracy', perf.get('f1_weighted', 0))
            if key_score >= 0.9:
                perf_assessment = "Excellent"
            elif key_score >= 0.8:
                perf_assessment = "Good"
            elif key_score >= 0.7:
                perf_assessment = "Fair"
            else:
                perf_assessment = "Poor"
        else:
            key_score = perf.get('r2', 0)
            if key_score >= 0.9:
                perf_assessment = "Excellent"
            elif key_score >= 0.7:
                perf_assessment = "Good" 
            elif key_score >= 0.5:
                perf_assessment = "Fair"
            else:
                perf_assessment = "Poor"
        
        print(f"📊 Model Performance: {perf_assessment} ({key_score:.3f})")
    
    # Stability assessment
    if 'cv_stability' in evaluation_results:
        cv_results = evaluation_results['cv_stability']
        avg_cv = np.mean([stats.get('cv', 1) for stats in cv_results.values() if isinstance(stats, dict)])
        
        if avg_cv < 0.05:
            stability_assessment = "Very Stable"
        elif avg_cv < 0.1:
            stability_assessment = "Stable"
        elif avg_cv < 0.2:
            stability_assessment = "Moderately Stable"
        else:
            stability_assessment = "Unstable"
        
        print(f"📈 Model Stability: {stability_assessment} (CV: {avg_cv:.3f})")
    
    # Fairness assessment
    if 'fairness_analysis' in evaluation_results:
        fairness = evaluation_results['fairness_analysis']
        max_disparity_overall = 1.0
        
        for attr_results in fairness.values():
            if 'disparities' in attr_results:
                disparities = attr_results['disparities']
                for disp_value in disparities.values():
                    if 'ratio' in str(disp_value):
                        max_disparity_overall = max(max_disparity_overall, disp_value)
        
        if max_disparity_overall > 1.5:
            fairness_assessment = "Significant Bias"
        elif max_disparity_overall > 1.2:
            fairness_assessment = "Some Bias"
        else:
            fairness_assessment = "Fair"
        
        print(f"⚖️  Fairness Assessment: {fairness_assessment} (Max Ratio: {max_disparity_overall:.2f})")
    
    # Recommendations
    print()
    print("RECOMMENDATIONS:")
    print("-" * 15)
    
    recommendations = _generate_recommendations(evaluation_results)
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    
    print("=" * 80)


def _generate_recommendations(evaluation_results: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on evaluation results."""
    recommendations = []
    
    # Performance-based recommendations
    if 'performance' in evaluation_results:
        perf = evaluation_results['performance']
        task_type = evaluation_results['task_type']
        
        if task_type == 'classification':
            accuracy = perf.get('accuracy', 0)
            if accuracy < 0.7:
                recommendations.append(
                    "Consider feature engineering, different algorithms, or more data"
                )
            elif accuracy > 0.95:
                recommendations.append(
                    "Excellent performance - validate on additional datasets to check for overfitting"
                )
        else:
            r2 = perf.get('r2', 0)
            if r2 < 0.5:
                recommendations.append(
                    "Low R² suggests model may not capture relationships well - try feature engineering"
                )
            elif r2 > 0.95:
                recommendations.append(
                    "Very high R² - validate this isn't due to data leakage or overfitting"
                )
    
    # Stability recommendations
    if 'cv_stability' in evaluation_results:
        cv_results = evaluation_results['cv_stability']
        avg_cv = np.mean([stats.get('cv', 0) for stats in cv_results.values() if isinstance(stats, dict)])
        
        if avg_cv > 0.2:
            recommendations.append(
                "High cross-validation variance suggests overfitting - try regularization or more data"
            )
    
    # Feature importance recommendations
    if 'feature_importance' in evaluation_results:
        fi = evaluation_results['feature_importance']
        n_features = evaluation_results['n_features']
        
        if 'permutation_importance' in fi:
            importances = fi['permutation_importance']['importances_mean']
            # Check if many features have near-zero importance
            low_importance_features = sum(1 for imp in importances if imp < 0.01)
            if low_importance_features > n_features * 0.5:
                recommendations.append(
                    f"{low_importance_features} features show low importance - consider feature selection"
                )
    
    # Error analysis recommendations
    if 'error_analysis' in evaluation_results:
        error = evaluation_results['error_analysis']
        
        if evaluation_results['task_type'] == 'regression':
            if 'residuals_mean' in error and abs(error['residuals_mean']) > 0.1:
                recommendations.append(
                    "Non-zero mean residuals suggest systematic bias - check for missing features"
                )
    
    # Fairness recommendations
    if 'fairness_analysis' in evaluation_results:
        fairness = evaluation_results['fairness_analysis']
        
        for attr_name, attr_results in fairness.items():
            if 'disparities' in attr_results:
                disparities = attr_results['disparities']
                max_disparity = max([v for k, v in disparities.items() if 'ratio' in k], default=1.0)
                
                if max_disparity > 1.5:
                    recommendations.append(
                        f"Significant fairness disparity for {attr_name} - consider bias mitigation techniques"
                    )
                elif max_disparity > 1.2:
                    recommendations.append(
                        f"Monitor fairness for {attr_name} - consider additional evaluation"
                    )
    
    # Default recommendation if none generated
    if not recommendations:
        recommendations.append(
            "Model shows good overall performance - proceed with deployment monitoring"
        )
    
    return recommendations


def create_feature_importance_report(evaluation_results: Dict[str, Any]) -> Optional[pd.DataFrame]:
    """
    Create a detailed feature importance report.
    
    Parameters
    ----------
    evaluation_results : dict
        Results from final_model_evaluation function
        
    Returns
    -------
    pd.DataFrame or None
        Feature importance report
    """
    if 'feature_importance' not in evaluation_results:
        return None
    
    fi = evaluation_results['feature_importance']
    feature_names = evaluation_results['feature_names']
    
    # Combine different importance measures
    importance_data = []
    
    for feature_idx, feature_name in enumerate(feature_names):
        row = {'Feature': feature_name}
        
        # Built-in importance
        if 'builtin_importance' in fi:
            builtin_values = fi['builtin_importance']['values']
            if feature_idx < len(builtin_values):
                row['Built_in_Importance'] = builtin_values[feature_idx]
        
        # Permutation importance
        if 'permutation_importance' in fi:
            perm_mean = fi['permutation_importance']['importances_mean']
            perm_std = fi['permutation_importance']['importances_std']
            if feature_idx < len(perm_mean):
                row['Permutation_Importance'] = perm_mean[feature_idx]
                row['Permutation_Std'] = perm_std[feature_idx]
        
        # Feature correlation
        if 'feature_correlations' in fi:
            correlations = fi['feature_correlations']['correlations']
            if feature_idx < len(correlations):
                row['Target_Correlation'] = correlations[feature_idx]
        
        importance_data.append(row)
    
    df = pd.DataFrame(importance_data)
    
    # Add rankings
    if 'Built_in_Importance' in df.columns:
        df['Built_in_Rank'] = df['Built_in_Importance'].rank(ascending=False, method='dense')
    
    if 'Permutation_Importance' in df.columns:
        df['Permutation_Rank'] = df['Permutation_Importance'].rank(ascending=False, method='dense')
    
    # Sort by most available importance measure
    if 'Permutation_Importance' in df.columns:
        df = df.sort_values('Permutation_Importance', ascending=False)
    elif 'Built_in_Importance' in df.columns:
        df = df.sort_values('Built_in_Importance', ascending=False)
    
    return df


def create_fairness_report(evaluation_results: Dict[str, Any]) -> Optional[pd.DataFrame]:
    """
    Create a detailed fairness analysis report.
    
    Parameters
    ----------
    evaluation_results : dict
        Results from final_model_evaluation function
        
    Returns
    -------
    pd.DataFrame or None
        Fairness analysis report
    """
    if 'fairness_analysis' not in evaluation_results:
        return None
    
    fairness = evaluation_results['fairness_analysis']
    fairness_data = []
    
    for attr_name, attr_results in fairness.items():
        if 'group_metrics' in attr_results:
            group_metrics = attr_results['group_metrics']
            
            for group, metrics in group_metrics.items():
                row = {
                    'Protected_Attribute': attr_name,
                    'Group': group,
                    'Sample_Size': metrics.get('size', 0)
                }
                
                # Add all available metrics
                for metric_name, metric_value in metrics.items():
                    if metric_name not in ['size']:
                        row[metric_name.title()] = metric_value
                
                fairness_data.append(row)
    
    if not fairness_data:
        return None
    
    df = pd.DataFrame(fairness_data)
    return df