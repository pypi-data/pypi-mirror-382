"""
Comprehensive model evaluation including hold-out testing, interpretation, 
feature importance, error analysis, and fairness evaluation.
"""
import numpy as np
import pandas as pd
from sklearn.model_selection import cross_validate
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    mean_squared_error, mean_absolute_error, r2_score, explained_variance_score
)
from sklearn.inspection import permutation_importance
from sklearn.calibration import calibration_curve
from typing import Union, Optional, Dict, Any, List, Tuple
import warnings
import contextlib


@contextlib.contextmanager
def _suppress_sklearn_warnings():
    """Context manager to suppress common sklearn warnings."""
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=UserWarning)
        warnings.filterwarnings('ignore', message='.*feature names.*')
        warnings.filterwarnings('ignore', message='.*valid feature names.*')
        warnings.filterwarnings('ignore', message='.*StandardScaler.*')
        warnings.filterwarnings('ignore', message='.*OneHotEncoder.*')
        warnings.filterwarnings('ignore', message='.*does not have valid feature names.*')
        yield


def final_model_evaluation(
    model,
    X_train: Union[pd.DataFrame, np.ndarray],
    y_train: Union[pd.Series, np.ndarray],
    X_test: Union[pd.DataFrame, np.ndarray],
    y_test: Union[pd.Series, np.ndarray],
    task_type: str = 'auto',
    cv_folds: int = 5,
    feature_names: Optional[List[str]] = None,
    protected_attributes: Optional[Dict[str, Union[pd.Series, np.ndarray]]] = None,
    random_state: int = 42,
    suppress_warnings: bool = False
) -> Dict[str, Any]:
    """
    Comprehensive final model evaluation on hold-out test set.
    
    Parameters
    ----------
    model : estimator object
        The trained model to evaluate
    X_train : array-like of shape (n_samples_train, n_features)
        Training features
    y_train : array-like of shape (n_samples_train,)
        Training targets
    X_test : array-like of shape (n_samples_test, n_features)
        Test features  
    y_test : array-like of shape (n_samples_test,)
        Test targets
    task_type : str, default='auto'
        Type of ML task: 'classification', 'regression', or 'auto'
    cv_folds : int, default=5
        Number of cross-validation folds for stability analysis
    feature_names : list of str, optional
        Names of features for interpretability
    protected_attributes : dict, optional
        Protected attributes for fairness analysis
        Format: {'attribute_name': array_of_values}
    random_state : int, default=42
        Random state for reproducibility
    suppress_warnings : bool, default=False
        If True, suppresses sklearn warnings about feature names and other non-critical warnings
        
    Returns
    -------
    dict
        Comprehensive evaluation results
    """
    # Use context manager for warning suppression if requested
    context = _suppress_sklearn_warnings() if suppress_warnings else contextlib.nullcontext()
    
    with context:
        # Determine task type
        if task_type == 'auto':
            task_type = _detect_task_type(y_train)
        
        # Validate inputs
        _validate_evaluation_inputs(model, X_train, y_train, X_test, y_test)
        
        # Get feature names
        if feature_names is None:
            if hasattr(X_train, 'columns'):
                feature_names = list(X_train.columns)
            else:
                feature_names = [f'feature_{i}' for i in range(X_train.shape[1])]
        
        # Convert to arrays for consistency
        X_train_array = np.asarray(X_train)
        y_train_array = np.asarray(y_train)
        X_test_array = np.asarray(X_test)
        y_test_array = np.asarray(y_test)
        
        # Initialize results dictionary
        results = {
            'task_type': task_type,
            'train_size': len(X_train_array),
            'test_size': len(X_test_array),
            'n_features': X_train_array.shape[1],
            'feature_names': feature_names
        }
        
        # 1. Basic Performance Metrics
        results['performance'] = _evaluate_basic_performance(
            model, X_test_array, y_test_array, task_type
        )
        
        # 2. Cross-validation stability on training set
        results['cv_stability'] = _evaluate_cv_stability(
            model, X_train_array, y_train_array, task_type, cv_folds
        )
        
        # 3. Feature Importance Analysis
        results['feature_importance'] = _analyze_feature_importance(
            model, X_train_array, y_train_array, X_test_array, y_test_array,
            feature_names, task_type, random_state
        )
        
        # 4. Error Analysis
        results['error_analysis'] = _analyze_errors(
            model, X_test_array, y_test_array, feature_names, task_type
        )
        
        # 5. Fairness Analysis (if protected attributes provided)
        if protected_attributes is not None:
            results['fairness_analysis'] = _analyze_fairness(
                model, X_test_array, y_test_array, protected_attributes, task_type
            )
        
        # 6. Model Interpretation
        results['interpretation'] = _analyze_model_interpretation(
            model, X_train_array, y_train_array, X_test_array, 
            feature_names, task_type, random_state
        )
        
        return results


def _detect_task_type(y: np.ndarray) -> str:
    """Detect whether this is a classification or regression task."""
    y_array = np.asarray(y)
    
    # Check if target is continuous or discrete
    unique_values = np.unique(y_array)
    n_unique = len(unique_values)
    
    # Heuristics for task detection
    if n_unique <= 20:  # Likely classification
        return 'classification'
    elif np.all(np.equal(np.mod(y_array, 1), 0)):  # All integers
        if n_unique <= 50:
            return 'classification'
        else:
            return 'regression'
    else:  # Contains floats
        return 'regression'


def _validate_evaluation_inputs(model, X_train, y_train, X_test, y_test):
    """Validate inputs for evaluation."""
    if not hasattr(model, 'fit') or not hasattr(model, 'predict'):
        raise ValueError("Model must have 'fit' and 'predict' methods")
    
    X_train_array = np.asarray(X_train)
    X_test_array = np.asarray(X_test)
    
    if X_train_array.shape[1] != X_test_array.shape[1]:
        raise ValueError(
            f"Training and test sets must have same number of features. "
            f"Got {X_train_array.shape[1]} and {X_test_array.shape[1]}"
        )
    
    if len(X_train_array) != len(y_train):
        raise ValueError("X_train and y_train must have same number of samples")
    
    if len(X_test_array) != len(y_test):
        raise ValueError("X_test and y_test must have same number of samples")


def _evaluate_basic_performance(
    model, X_test: np.ndarray, y_test: np.ndarray, task_type: str
) -> Dict[str, Any]:
    """Evaluate basic performance metrics."""
    y_pred = model.predict(X_test)
    
    if task_type == 'classification':
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision_macro': precision_score(y_test, y_pred, average='macro', zero_division=0),
            'recall_macro': recall_score(y_test, y_pred, average='macro', zero_division=0),
            'f1_macro': f1_score(y_test, y_pred, average='macro', zero_division=0),
            'precision_weighted': precision_score(y_test, y_pred, average='weighted', zero_division=0),
            'recall_weighted': recall_score(y_test, y_pred, average='weighted', zero_division=0),
            'f1_weighted': f1_score(y_test, y_pred, average='weighted', zero_division=0)
        }
        
        # Add ROC AUC for binary classification
        unique_labels = np.unique(y_test)
        if len(unique_labels) == 2:
            try:
                if hasattr(model, 'predict_proba'):
                    y_proba = model.predict_proba(X_test)[:, 1]
                elif hasattr(model, 'decision_function'):
                    y_proba = model.decision_function(X_test)
                else:
                    y_proba = y_pred
                metrics['roc_auc'] = roc_auc_score(y_test, y_proba)
            except Exception:
                pass
        
        # Class distribution
        unique, counts = np.unique(y_test, return_counts=True)
        metrics['class_distribution'] = dict(zip(unique, counts))
        
    else:  # regression
        metrics = {
            'mse': mean_squared_error(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'mae': mean_absolute_error(y_test, y_pred),
            'r2': r2_score(y_test, y_pred),
            'explained_variance': explained_variance_score(y_test, y_pred)
        }
        
        # Additional regression metrics
        residuals = y_test - y_pred
        metrics.update({
            'mean_residual': np.mean(residuals),
            'std_residual': np.std(residuals),
            'mean_abs_error': np.mean(np.abs(residuals)),
            'median_abs_error': np.median(np.abs(residuals)),
            'max_error': np.max(np.abs(residuals))
        })
    
    return metrics


def _evaluate_cv_stability(
    model, X_train: np.ndarray, y_train: np.ndarray, 
    task_type: str, cv_folds: int
) -> Dict[str, Any]:
    """Evaluate model stability using cross-validation."""
    if task_type == 'classification':
        scoring = ['accuracy', 'precision_macro', 'recall_macro', 'f1_macro']
    else:
        scoring = ['neg_mean_squared_error', 'neg_mean_absolute_error', 'r2']
    
    try:
        cv_results = cross_validate(
            model, X_train, y_train, cv=cv_folds,
            scoring=scoring, return_train_score=False
        )
        
        stability_metrics = {}
        for metric in scoring:
            scores = cv_results[f'test_{metric}']
            if metric.startswith('neg_'):
                scores = -scores  # Convert negative scores to positive
                metric_name = metric[4:]  # Remove 'neg_' prefix
            else:
                metric_name = metric
            
            stability_metrics[metric_name] = {
                'mean': np.mean(scores),
                'std': np.std(scores),
                'min': np.min(scores),
                'max': np.max(scores),
                'cv': np.std(scores) / np.mean(scores) if np.mean(scores) != 0 else 0
            }
        
        return stability_metrics
        
    except Exception as e:
        warnings.warn(f"Cross-validation stability analysis failed: {e}")
        return {}


def _analyze_feature_importance(
    model, X_train: np.ndarray, y_train: np.ndarray, 
    X_test: np.ndarray, y_test: np.ndarray,
    feature_names: List[str], task_type: str, random_state: int
) -> Dict[str, Any]:
    """Analyze feature importance using multiple methods."""
    importance_results = {}
    
    # 1. Built-in feature importance (for tree-based models)
    if hasattr(model, 'feature_importances_'):
        importance_results['builtin_importance'] = {
            'values': model.feature_importances_.tolist(),
            'features': feature_names
        }
    
    # 2. Permutation importance (model-agnostic)
    try:
        if task_type == 'classification':
            scoring = 'accuracy'
        else:
            scoring = 'r2'
        
        perm_importance = permutation_importance(
            model, X_test, y_test, n_repeats=10, 
            random_state=random_state, scoring=scoring
        )
        
        importance_results['permutation_importance'] = {
            'importances_mean': perm_importance.importances_mean.tolist(),
            'importances_std': perm_importance.importances_std.tolist(),
            'features': feature_names
        }
        
    except Exception as e:
        warnings.warn(f"Permutation importance calculation failed: {e}")
    
    # 3. Feature correlation with target
    try:
        correlations = []
        y_numeric = y_train if task_type == 'regression' else y_train.astype(float)
        
        for i in range(X_train.shape[1]):
            corr = np.corrcoef(X_train[:, i], y_numeric)[0, 1]
            correlations.append(corr if not np.isnan(corr) else 0.0)
        
        importance_results['feature_correlations'] = {
            'correlations': correlations,
            'features': feature_names
        }
        
    except Exception as e:
        warnings.warn(f"Feature correlation calculation failed: {e}")
    
    return importance_results


def _analyze_errors(
    model, X_test: np.ndarray, y_test: np.ndarray, 
    feature_names: List[str], task_type: str
) -> Dict[str, Any]:
    """Analyze prediction errors and patterns."""
    y_pred = model.predict(X_test)
    error_analysis = {}
    
    if task_type == 'classification':
        # Confusion matrix analysis
        from sklearn.metrics import confusion_matrix, classification_report
        
        cm = confusion_matrix(y_test, y_pred)
        error_analysis['confusion_matrix'] = cm.tolist()
        
        # Classification report
        try:
            clf_report = classification_report(y_test, y_pred, output_dict=True)
            error_analysis['classification_report'] = clf_report
        except Exception:
            pass
        
        # Misclassification analysis
        misclassified_indices = np.where(y_test != y_pred)[0]
        error_analysis['misclassification_rate'] = len(misclassified_indices) / len(y_test)
        error_analysis['n_misclassified'] = len(misclassified_indices)
        
        # Error patterns by feature ranges (if feasible)
        if len(misclassified_indices) > 0 and X_test.shape[1] <= 20:  # Limit for performance
            error_patterns = []
            for i, feature_name in enumerate(feature_names):
                feature_values = X_test[:, i]
                misclassified_values = feature_values[misclassified_indices]
                
                pattern = {
                    'feature': feature_name,
                    'error_mean': np.mean(misclassified_values),
                    'error_std': np.std(misclassified_values),
                    'overall_mean': np.mean(feature_values),
                    'overall_std': np.std(feature_values)
                }
                error_patterns.append(pattern)
            
            error_analysis['error_patterns_by_feature'] = error_patterns
    
    else:  # regression
        residuals = y_test - y_pred
        error_analysis.update({
            'residuals_mean': np.mean(residuals),
            'residuals_std': np.std(residuals),
            'residuals_skewness': _calculate_skewness(residuals),
            'residuals_kurtosis': _calculate_kurtosis(residuals),
            'abs_residuals_mean': np.mean(np.abs(residuals)),
            'abs_residuals_median': np.median(np.abs(residuals))
        })
        
        # Large error analysis
        large_errors_threshold = np.percentile(np.abs(residuals), 90)
        large_error_indices = np.where(np.abs(residuals) > large_errors_threshold)[0]
        
        error_analysis['large_errors'] = {
            'threshold': large_errors_threshold,
            'n_large_errors': len(large_error_indices),
            'large_error_rate': len(large_error_indices) / len(y_test)
        }
        
        # Error correlation with features
        if X_test.shape[1] <= 20 and X_test.shape[0] >= 2:  # Need at least 2 samples for correlation
            error_correlations = []
            for i, feature_name in enumerate(feature_names):
                try:
                    feature_values = X_test[:, i]
                    abs_residuals = np.abs(residuals)
                    
                    # Ensure we have arrays with at least 2 elements and some variance
                    if (len(feature_values) >= 2 and len(abs_residuals) >= 2 and 
                        np.std(feature_values) > 1e-8 and np.std(abs_residuals) > 1e-8):
                        corr = np.corrcoef(feature_values, abs_residuals)[0, 1]
                        if np.isnan(corr):
                            corr = 0.0
                    else:
                        corr = 0.0
                        
                    error_correlations.append({
                        'feature': feature_name,
                        'error_correlation': corr
                    })
                except Exception:
                    # If correlation calculation fails for any reason, set to 0
                    error_correlations.append({
                        'feature': feature_name,
                        'error_correlation': 0.0
                    })
            
            error_analysis['error_correlations_with_features'] = error_correlations
    
    return error_analysis


def _analyze_fairness(
    model, X_test: np.ndarray, y_test: np.ndarray, 
    protected_attributes: Dict[str, Union[pd.Series, np.ndarray]], 
    task_type: str
) -> Dict[str, Any]:
    """Analyze fairness metrics across protected groups."""
    y_pred = model.predict(X_test)
    fairness_results = {}
    
    for attr_name, attr_values in protected_attributes.items():
        attr_array = np.asarray(attr_values)
        
        if len(attr_array) != len(y_test):
            warnings.warn(f"Protected attribute '{attr_name}' length doesn't match test set")
            continue
        
        unique_groups = np.unique(attr_array)
        group_metrics = {}
        
        for group in unique_groups:
            group_mask = attr_array == group
            group_y_test = y_test[group_mask]
            group_y_pred = y_pred[group_mask]
            
            if len(group_y_test) == 0:
                continue
            
            if task_type == 'classification':
                group_metrics[str(group)] = {
                    'accuracy': accuracy_score(group_y_test, group_y_pred),
                    'precision': precision_score(group_y_test, group_y_pred, average='weighted', zero_division=0),
                    'recall': recall_score(group_y_test, group_y_pred, average='weighted', zero_division=0),
                    'f1': f1_score(group_y_test, group_y_pred, average='weighted', zero_division=0),
                    'positive_rate': np.mean(group_y_pred == 1) if len(np.unique(group_y_test)) == 2 else None,
                    'size': len(group_y_test)
                }
                
                # TPR and FPR for binary classification
                if len(np.unique(group_y_test)) == 2:
                    tp = np.sum((group_y_test == 1) & (group_y_pred == 1))
                    fp = np.sum((group_y_test == 0) & (group_y_pred == 1))
                    fn = np.sum((group_y_test == 1) & (group_y_pred == 0))
                    tn = np.sum((group_y_test == 0) & (group_y_pred == 0))
                    
                    group_metrics[str(group)].update({
                        'tpr': tp / (tp + fn) if (tp + fn) > 0 else 0,
                        'fpr': fp / (fp + tn) if (fp + tn) > 0 else 0,
                        'tnr': tn / (tn + fp) if (tn + fp) > 0 else 0,
                        'fnr': fn / (fn + tp) if (fn + tp) > 0 else 0
                    })
                
            else:  # regression
                residuals = group_y_test - group_y_pred
                group_metrics[str(group)] = {
                    'mse': mean_squared_error(group_y_test, group_y_pred),
                    'mae': mean_absolute_error(group_y_test, group_y_pred),
                    'r2': r2_score(group_y_test, group_y_pred),
                    'mean_residual': np.mean(residuals),
                    'abs_mean_residual': np.mean(np.abs(residuals)),
                    'size': len(group_y_test)
                }
        
        # Calculate fairness disparities
        if len(group_metrics) >= 2:
            disparities = _calculate_fairness_disparities(group_metrics, task_type)
            fairness_results[attr_name] = {
                'group_metrics': group_metrics,
                'disparities': disparities
            }
        
    return fairness_results


def _calculate_fairness_disparities(
    group_metrics: Dict[str, Dict[str, float]], task_type: str
) -> Dict[str, float]:
    """Calculate fairness disparities between groups."""
    disparities = {}
    
    # Get all metric values by group
    groups = list(group_metrics.keys())
    
    if task_type == 'classification':
        metrics_to_check = ['accuracy', 'precision', 'recall', 'f1']
        if 'positive_rate' in group_metrics[groups[0]] and group_metrics[groups[0]]['positive_rate'] is not None:
            metrics_to_check.append('positive_rate')
        if 'tpr' in group_metrics[groups[0]]:
            metrics_to_check.extend(['tpr', 'fpr'])
    else:
        metrics_to_check = ['mse', 'mae', 'r2', 'abs_mean_residual']
    
    for metric in metrics_to_check:
        values = []
        for group in groups:
            if metric in group_metrics[group] and group_metrics[group][metric] is not None:
                values.append(group_metrics[group][metric])
        
        if len(values) >= 2:
            disparities[f'{metric}_ratio'] = max(values) / (min(values) + 1e-8)
            disparities[f'{metric}_difference'] = max(values) - min(values)
    
    return disparities


def _analyze_model_interpretation(
    model, X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray,
    feature_names: List[str], task_type: str, random_state: int
) -> Dict[str, Any]:
    """Analyze model interpretability aspects."""
    interpretation_results = {}
    
    # Model complexity metrics
    interpretation_results['model_complexity'] = _assess_model_complexity(model)
    
    # Feature interactions (if feasible)
    if X_train.shape[1] <= 10:  # Limit for computational feasibility
        interpretation_results['feature_interactions'] = _analyze_feature_interactions(
            model, X_train, y_train, feature_names, task_type, random_state
        )
    
    # Prediction confidence analysis
    interpretation_results['prediction_confidence'] = _analyze_prediction_confidence(
        model, X_test, task_type
    )
    
    return interpretation_results


def _assess_model_complexity(model) -> Dict[str, Any]:
    """Assess model complexity metrics."""
    complexity = {'model_type': type(model).__name__}
    
    # Tree-based model complexity
    if hasattr(model, 'n_estimators'):
        complexity['n_estimators'] = model.n_estimators
    
    if hasattr(model, 'max_depth'):
        complexity['max_depth'] = model.max_depth
    
    if hasattr(model, 'tree_') and hasattr(model.tree_, 'node_count'):
        complexity['n_nodes'] = model.tree_.node_count
        if hasattr(model.tree_, 'n_leaves'):
            complexity['n_leaves'] = model.tree_.n_leaves
    
    # Linear model complexity
    if hasattr(model, 'coef_'):
        coef = np.asarray(model.coef_)
        complexity['n_features_used'] = np.sum(coef != 0)
        complexity['l1_norm'] = np.sum(np.abs(coef))
        complexity['l2_norm'] = np.sqrt(np.sum(coef ** 2))
    
    return complexity


def _analyze_feature_interactions(
    model, X_train: np.ndarray, y_train: np.ndarray,
    feature_names: List[str], task_type: str, random_state: int
) -> Dict[str, Any]:
    """Analyze potential feature interactions."""
    interactions = {}
    n_features = X_train.shape[1]
    
    # Sample a subset for computational efficiency
    if len(X_train) > 1000:
        indices = np.random.RandomState(random_state).choice(
            len(X_train), size=1000, replace=False
        )
        X_sample = X_train[indices]
        y_sample = y_train[indices]
    else:
        X_sample = X_train
        y_sample = y_train
    
    # Simple pairwise interaction detection
    interaction_strengths = []
    
    # Need at least 2 samples for correlation calculation
    if len(X_sample) >= 2:
        for i in range(n_features):
            for j in range(i + 1, n_features):
                try:
                    # Create interaction feature
                    interaction_feature = X_sample[:, i] * X_sample[:, j]
                    
                    # Ensure we have valid arrays with variance for correlation
                    if (len(interaction_feature) >= 2 and len(y_sample) >= 2 and
                        np.std(interaction_feature) > 1e-8 and np.std(y_sample) > 1e-8):
                        
                        # Calculate correlation with target
                        if task_type == 'regression':
                            corr = np.corrcoef(interaction_feature, y_sample)[0, 1]
                        else:
                            corr = np.corrcoef(interaction_feature, y_sample.astype(float))[0, 1]
                        
                        if not np.isnan(corr):
                            interaction_strengths.append({
                                'feature_1': feature_names[i],
                                'feature_2': feature_names[j],
                                'interaction_strength': abs(corr)
                            })
                    
                except Exception:
                    # Skip this interaction if correlation calculation fails
                    continue
    
    # Sort by interaction strength
    interaction_strengths.sort(key=lambda x: x['interaction_strength'], reverse=True)
    interactions['pairwise_interactions'] = interaction_strengths[:10]  # Top 10
    
    return interactions


def _analyze_prediction_confidence(model, X_test: np.ndarray, task_type: str) -> Dict[str, Any]:
    """Analyze prediction confidence and calibration."""
    confidence_analysis = {}
    
    if task_type == 'classification':
        if hasattr(model, 'predict_proba'):
            y_proba = model.predict_proba(X_test)
            
            # Prediction confidence distribution
            max_proba = np.max(y_proba, axis=1)
            confidence_analysis.update({
                'mean_confidence': np.mean(max_proba),
                'std_confidence': np.std(max_proba),
                'min_confidence': np.min(max_proba),
                'max_confidence': np.max(max_proba),
                'confidence_quartiles': np.percentile(max_proba, [25, 50, 75]).tolist()
            })
            
            # Low confidence predictions
            low_confidence_threshold = np.percentile(max_proba, 10)
            n_low_confidence = np.sum(max_proba < low_confidence_threshold)
            confidence_analysis.update({
                'low_confidence_threshold': low_confidence_threshold,
                'n_low_confidence_predictions': n_low_confidence,
                'low_confidence_rate': n_low_confidence / len(X_test)
            })
    
    else:  # regression
        # For regression, we can analyze prediction intervals if supported
        if hasattr(model, 'predict') and hasattr(model, 'score'):
            y_pred = model.predict(X_test)
            confidence_analysis.update({
                'prediction_range': {
                    'min': np.min(y_pred),
                    'max': np.max(y_pred),
                    'mean': np.mean(y_pred),
                    'std': np.std(y_pred)
                }
            })
    
    return confidence_analysis


def _calculate_skewness(data: np.ndarray) -> float:
    """Calculate skewness of data."""
    try:
        from scipy import stats
        return stats.skew(data)
    except ImportError:
        # Simple skewness calculation
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0.0
        return np.mean(((data - mean) / std) ** 3)


def _calculate_kurtosis(data: np.ndarray) -> float:
    """Calculate kurtosis of data."""
    try:
        from scipy import stats
        return stats.kurtosis(data)
    except ImportError:
        # Simple kurtosis calculation
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0.0
        return np.mean(((data - mean) / std) ** 4) - 3