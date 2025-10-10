"""
ROC curve analysis and threshold optimization for classification models
"""
import numpy as np
import pandas as pd
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import roc_curve, auc, precision_recall_curve, average_precision_score
from sklearn.preprocessing import label_binarize
from sklearn.multiclass import OneVsRestClassifier
from typing import Union, Optional, Tuple, Dict, Any, List
import warnings


def calculate_roc_metrics(
    model,
    X: Union[pd.DataFrame, np.ndarray],
    y: Union[pd.Series, np.ndarray],
    cv: int = 5,
    pos_label: Optional[Union[int, str]] = None
) -> Dict[str, Any]:
    """
    Calculate ROC curve metrics and data for binary classification.
    
    Parameters
    ----------
    model : estimator object
        The fitted classification model
    X : array-like of shape (n_samples, n_features)
        Feature data
    y : array-like of shape (n_samples,)
        Target values (binary labels)
    cv : int, default=5
        Number of cross-validation folds for predictions
    pos_label : int or str, optional
        Label of positive class for binary classification
        
    Returns
    -------
    dict
        Dictionary containing ROC analysis results
    """
    # Validate inputs
    y_array = np.asarray(y)
    unique_labels = np.unique(y_array)
    n_classes = len(unique_labels)
    
    if n_classes != 2:
        raise ValueError(f"Binary classification expected, got {n_classes} classes")
    
    # Determine positive label
    if pos_label is None:
        pos_label = unique_labels[1]  # Use second label as positive by default
    
    # Get cross-validated predicted probabilities
    try:
        y_proba = cross_val_predict(model, X, y, cv=cv, method='predict_proba')
        # Get probabilities for positive class
        pos_label_index = list(unique_labels).index(pos_label)
        y_scores = y_proba[:, pos_label_index]
    except (AttributeError, NotImplementedError):
        # Fallback to decision function if predict_proba not available
        y_scores = cross_val_predict(model, X, y, cv=cv, method='decision_function')
    
    # Calculate ROC curve
    fpr, tpr, thresholds = roc_curve(y, y_scores, pos_label=pos_label)
    roc_auc = auc(fpr, tpr)
    
    # Find optimal threshold using Youden's Index (max(TPR - FPR))
    youden_index = tpr - fpr
    optimal_idx = np.argmax(youden_index)
    optimal_threshold = thresholds[optimal_idx]
    optimal_tpr = tpr[optimal_idx]
    optimal_fpr = fpr[optimal_idx]
    
    # Calculate other threshold metrics
    threshold_metrics = []
    for i, thresh in enumerate(thresholds):
        threshold_metrics.append({
            'threshold': thresh,
            'fpr': fpr[i],
            'tpr': tpr[i],
            'tnr': 1 - fpr[i],  # True Negative Rate (Specificity)
            'fnr': 1 - tpr[i],  # False Negative Rate
            'youden_index': tpr[i] - fpr[i],
            'distance_to_perfect': np.sqrt((fpr[i] - 0)**2 + (tpr[i] - 1)**2)  # Distance to (0,1)
        })
    
    # Create results dictionary
    results = {
        'fpr': fpr,
        'tpr': tpr,
        'thresholds': thresholds,
        'roc_auc': roc_auc,
        'optimal_threshold': optimal_threshold,
        'optimal_tpr': optimal_tpr,
        'optimal_fpr': optimal_fpr,
        'optimal_youden_index': youden_index[optimal_idx],
        'threshold_metrics': pd.DataFrame(threshold_metrics),
        'y_scores': y_scores,
        'y_true': y_array,
        'pos_label': pos_label,
        'n_samples': len(y_array)
    }
    
    return results


def calculate_multiclass_roc_metrics(
    model,
    X: Union[pd.DataFrame, np.ndarray],
    y: Union[pd.Series, np.ndarray],
    cv: int = 5
) -> Dict[str, Any]:
    """
    Calculate ROC curve metrics for multiclass classification using one-vs-rest approach.
    
    Parameters
    ----------
    model : estimator object
        The fitted classification model
    X : array-like of shape (n_samples, n_features)
        Feature data
    y : array-like of shape (n_samples,)
        Target values (multiclass labels)
    cv : int, default=5
        Number of cross-validation folds for predictions
        
    Returns
    -------
    dict
        Dictionary containing multiclass ROC analysis results
    """
    y_array = np.asarray(y)
    unique_labels = np.unique(y_array)
    n_classes = len(unique_labels)
    
    if n_classes < 3:
        raise ValueError(f"Multiclass classification expected (≥3 classes), got {n_classes} classes")
    
    # Get cross-validated predicted probabilities
    try:
        y_proba = cross_val_predict(model, X, y, cv=cv, method='predict_proba')
    except (AttributeError, NotImplementedError):
        raise ValueError("Model must support predict_proba for multiclass ROC analysis")
    
    # Binarize labels for one-vs-rest
    y_binarized = label_binarize(y_array, classes=unique_labels)
    
    # Calculate ROC curve for each class
    class_results = {}
    fpr_dict = {}
    tpr_dict = {}
    roc_auc_dict = {}
    
    for i, class_label in enumerate(unique_labels):
        fpr, tpr, thresholds = roc_curve(y_binarized[:, i], y_proba[:, i])
        roc_auc = auc(fpr, tpr)
        
        # Find optimal threshold for this class
        youden_index = tpr - fpr
        optimal_idx = np.argmax(youden_index)
        
        class_results[class_label] = {
            'fpr': fpr,
            'tpr': tpr,
            'thresholds': thresholds,
            'roc_auc': roc_auc,
            'optimal_threshold': thresholds[optimal_idx],
            'optimal_tpr': tpr[optimal_idx],
            'optimal_fpr': fpr[optimal_idx],
            'optimal_youden_index': youden_index[optimal_idx]
        }
        
        fpr_dict[class_label] = fpr
        tpr_dict[class_label] = tpr
        roc_auc_dict[class_label] = roc_auc
    
    # Calculate micro-average ROC curve
    fpr_micro, tpr_micro, _ = roc_curve(y_binarized.ravel(), y_proba.ravel())
    roc_auc_micro = auc(fpr_micro, tpr_micro)
    
    # Calculate macro-average ROC curve
    # First aggregate all false positive rates
    all_fpr = np.unique(np.concatenate([fpr_dict[label] for label in unique_labels]))
    
    # Then interpolate all ROC curves at this points
    mean_tpr = np.zeros_like(all_fpr)
    for label in unique_labels:
        mean_tpr += np.interp(all_fpr, fpr_dict[label], tpr_dict[label])
    
    # Average it and compute AUC
    mean_tpr /= n_classes
    roc_auc_macro = auc(all_fpr, mean_tpr)
    
    # Compile results
    results = {
        'class_results': class_results,
        'micro_average': {
            'fpr': fpr_micro,
            'tpr': tpr_micro,
            'roc_auc': roc_auc_micro
        },
        'macro_average': {
            'fpr': all_fpr,
            'tpr': mean_tpr,
            'roc_auc': roc_auc_macro
        },
        'class_labels': unique_labels,
        'n_classes': n_classes,
        'n_samples': len(y_array),
        'y_proba': y_proba,
        'y_true': y_array
    }
    
    return results


def calculate_precision_recall_metrics(
    model,
    X: Union[pd.DataFrame, np.ndarray],
    y: Union[pd.Series, np.ndarray],
    cv: int = 5,
    pos_label: Optional[Union[int, str]] = None
) -> Dict[str, Any]:
    """
    Calculate Precision-Recall curve metrics for binary classification.
    
    Parameters
    ----------
    model : estimator object
        The fitted classification model
    X : array-like of shape (n_samples, n_features)
        Feature data
    y : array-like of shape (n_samples,)
        Target values (binary labels)
    cv : int, default=5
        Number of cross-validation folds for predictions
    pos_label : int or str, optional
        Label of positive class for binary classification
        
    Returns
    -------
    dict
        Dictionary containing PR analysis results
    """
    # Validate inputs
    y_array = np.asarray(y)
    unique_labels = np.unique(y_array)
    n_classes = len(unique_labels)
    
    if n_classes != 2:
        raise ValueError(f"Binary classification expected, got {n_classes} classes")
    
    # Determine positive label
    if pos_label is None:
        pos_label = unique_labels[1]
    
    # Get cross-validated predicted probabilities
    try:
        y_proba = cross_val_predict(model, X, y, cv=cv, method='predict_proba')
        pos_label_index = list(unique_labels).index(pos_label)
        y_scores = y_proba[:, pos_label_index]
    except (AttributeError, NotImplementedError):
        y_scores = cross_val_predict(model, X, y, cv=cv, method='decision_function')
    
    # Calculate Precision-Recall curve
    precision, recall, thresholds = precision_recall_curve(y, y_scores, pos_label=pos_label)
    pr_auc = average_precision_score(y, y_scores, pos_label=pos_label)
    
    # Find optimal threshold using F1 score
    f1_scores = 2 * (precision[:-1] * recall[:-1]) / (precision[:-1] + recall[:-1] + 1e-8)
    optimal_idx = np.argmax(f1_scores)
    optimal_threshold = thresholds[optimal_idx]
    optimal_precision = precision[optimal_idx]
    optimal_recall = recall[optimal_idx]
    optimal_f1 = f1_scores[optimal_idx]
    
    results = {
        'precision': precision,
        'recall': recall,
        'thresholds': thresholds,
        'pr_auc': pr_auc,
        'optimal_threshold': optimal_threshold,
        'optimal_precision': optimal_precision,
        'optimal_recall': optimal_recall,
        'optimal_f1': optimal_f1,
        'y_scores': y_scores,
        'y_true': y_array,
        'pos_label': pos_label,
        'n_samples': len(y_array)
    }
    
    return results


def find_optimal_thresholds(
    roc_metrics: Dict[str, Any],
    criteria: List[str] = ['youden', 'closest_to_perfect', 'balanced_accuracy']
) -> pd.DataFrame:
    """
    Find optimal thresholds using different criteria.
    
    Parameters
    ----------
    roc_metrics : dict
        Results from calculate_roc_metrics
    criteria : list of str
        Criteria to use for threshold optimization:
        - 'youden': Youden's Index (max TPR - FPR)
        - 'closest_to_perfect': Closest point to (0, 1)
        - 'balanced_accuracy': Max (TPR + TNR) / 2
        
    Returns
    -------
    pd.DataFrame
        DataFrame with optimal thresholds for each criterion
    """
    threshold_df = roc_metrics['threshold_metrics']
    results = []
    
    for criterion in criteria:
        if criterion == 'youden':
            optimal_idx = threshold_df['youden_index'].idxmax()
            description = "Maximizes TPR - FPR (Youden's Index)"
        elif criterion == 'closest_to_perfect':
            optimal_idx = threshold_df['distance_to_perfect'].idxmin()
            description = "Closest point to perfect classifier (0, 1)"
        elif criterion == 'balanced_accuracy':
            balanced_acc = (threshold_df['tpr'] + threshold_df['tnr']) / 2
            optimal_idx = balanced_acc.idxmax()
            description = "Maximizes (TPR + TNR) / 2"
        else:
            continue
        
        optimal_row = threshold_df.iloc[optimal_idx]
        results.append({
            'Criterion': criterion.replace('_', ' ').title(),
            'Description': description,
            'Threshold': optimal_row['threshold'],
            'TPR (Sensitivity)': optimal_row['tpr'],
            'FPR': optimal_row['fpr'],
            'TNR (Specificity)': optimal_row['tnr'],
            'Youden Index': optimal_row['youden_index']
        })
    
    return pd.DataFrame(results)


def create_threshold_analysis_report(
    roc_metrics: Dict[str, Any],
    pr_metrics: Optional[Dict[str, Any]] = None
) -> pd.DataFrame:
    """
    Create a comprehensive threshold analysis report.
    
    Parameters
    ----------
    roc_metrics : dict
        Results from calculate_roc_metrics
    pr_metrics : dict, optional
        Results from calculate_precision_recall_metrics
        
    Returns
    -------
    pd.DataFrame
        Comprehensive threshold analysis report
    """
    report_data = []
    
    # ROC Analysis Section
    report_data.extend([
        ['ROC Analysis', 'AUC Score', f"{roc_metrics['roc_auc']:.4f}", 
         'Area under ROC curve (0.5=random, 1.0=perfect)'],
        ['ROC Analysis', 'Optimal Threshold (Youden)', f"{roc_metrics['optimal_threshold']:.4f}",
         'Threshold maximizing TPR - FPR'],
        ['ROC Analysis', 'TPR at Optimal', f"{roc_metrics['optimal_tpr']:.4f}",
         'True Positive Rate at optimal threshold'],
        ['ROC Analysis', 'FPR at Optimal', f"{roc_metrics['optimal_fpr']:.4f}",
         'False Positive Rate at optimal threshold'],
        ['ROC Analysis', 'Youden Index', f"{roc_metrics['optimal_youden_index']:.4f}",
         'TPR - FPR at optimal threshold']
    ])
    
    # Precision-Recall Analysis Section
    if pr_metrics is not None:
        report_data.extend([
            ['PR Analysis', 'PR-AUC Score', f"{pr_metrics['pr_auc']:.4f}",
             'Area under Precision-Recall curve'],
            ['PR Analysis', 'Optimal Threshold (F1)', f"{pr_metrics['optimal_threshold']:.4f}",
             'Threshold maximizing F1 score'],
            ['PR Analysis', 'Precision at Optimal', f"{pr_metrics['optimal_precision']:.4f}",
             'Precision at optimal F1 threshold'],
            ['PR Analysis', 'Recall at Optimal', f"{pr_metrics['optimal_recall']:.4f}",
             'Recall at optimal F1 threshold'],
            ['PR Analysis', 'F1 Score at Optimal', f"{pr_metrics['optimal_f1']:.4f}",
             'F1 score at optimal threshold']
        ])
    
    # Sample Information
    report_data.extend([
        ['Sample Info', 'Total Samples', str(roc_metrics['n_samples']),
         'Number of samples in dataset'],
        ['Sample Info', 'Positive Label', str(roc_metrics['pos_label']),
         'Label used as positive class'],
        ['Sample Info', 'Score Range', 
         f"[{roc_metrics['y_scores'].min():.4f}, {roc_metrics['y_scores'].max():.4f}]",
         'Range of predicted scores/probabilities']
    ])
    
    df = pd.DataFrame(report_data, columns=['Category', 'Metric', 'Value', 'Description'])
    return df


def print_roc_auc_summary(
    roc_metrics: Dict[str, Any],
    pr_metrics: Optional[Dict[str, Any]] = None
) -> None:
    """
    Print a comprehensive ROC/AUC analysis summary.
    
    Parameters
    ----------
    roc_metrics : dict
        Results from calculate_roc_metrics
    pr_metrics : dict, optional
        Results from calculate_precision_recall_metrics
    """
    print("=" * 80)
    print("ROC CURVE AND AUC ANALYSIS REPORT")
    print("=" * 80)
    print(f"Dataset: {roc_metrics['n_samples']} samples")
    print(f"Positive class: {roc_metrics['pos_label']}")
    print()
    
    # ROC Analysis
    print("ROC CURVE ANALYSIS:")
    print("-" * 20)
    print(f"  AUC Score: {roc_metrics['roc_auc']:.4f}")
    
    # Interpret AUC
    auc_score = roc_metrics['roc_auc']
    if auc_score >= 0.9:
        auc_interpretation = "Excellent discrimination"
    elif auc_score >= 0.8:
        auc_interpretation = "Good discrimination"
    elif auc_score >= 0.7:
        auc_interpretation = "Fair discrimination"
    elif auc_score >= 0.6:
        auc_interpretation = "Poor discrimination"
    else:
        auc_interpretation = "Very poor discrimination"
    
    print(f"  Interpretation: {auc_interpretation}")
    print()
    
    # Optimal Threshold Analysis
    print("OPTIMAL THRESHOLD (Youden's Index):")
    print("-" * 35)
    print(f"  Threshold: {roc_metrics['optimal_threshold']:.4f}")
    print(f"  True Positive Rate:  {roc_metrics['optimal_tpr']:.4f} ({roc_metrics['optimal_tpr']*100:.1f}%)")
    print(f"  False Positive Rate: {roc_metrics['optimal_fpr']:.4f} ({roc_metrics['optimal_fpr']*100:.1f}%)")
    print(f"  True Negative Rate:  {1-roc_metrics['optimal_fpr']:.4f} ({(1-roc_metrics['optimal_fpr'])*100:.1f}%)")
    print(f"  Youden Index: {roc_metrics['optimal_youden_index']:.4f}")
    print()
    
    # Precision-Recall Analysis
    if pr_metrics is not None:
        print("PRECISION-RECALL ANALYSIS:")
        print("-" * 25)
        print(f"  PR-AUC Score: {pr_metrics['pr_auc']:.4f}")
        print(f"  Optimal Threshold (F1): {pr_metrics['optimal_threshold']:.4f}")
        print(f"  Precision at Optimal: {pr_metrics['optimal_precision']:.4f} ({pr_metrics['optimal_precision']*100:.1f}%)")
        print(f"  Recall at Optimal:    {pr_metrics['optimal_recall']:.4f} ({pr_metrics['optimal_recall']*100:.1f}%)")
        print(f"  F1 Score at Optimal:  {pr_metrics['optimal_f1']:.4f}")
        print()
    
    # Recommendations
    print("RECOMMENDATIONS:")
    print("-" * 15)
    
    if auc_score >= 0.8:
        print("✅ Good model performance:")
        print("   • Model shows good discriminative ability")
        print("   • Consider using optimal threshold for predictions")
        print("   • Validate performance on additional datasets")
    elif auc_score >= 0.7:
        print("⚠️  Fair model performance:")
        print("   • Model has moderate discriminative ability")
        print("   • Consider feature engineering or model tuning")
        print("   • Evaluate if threshold adjustment helps")
    else:
        print("❌ Poor model performance:")
        print("   • Model shows poor discriminative ability")
        print("   • Consider different algorithms or feature engineering")
        print("   • Review data quality and class balance")
    
    # Threshold recommendations
    if pr_metrics is not None:
        roc_thresh = roc_metrics['optimal_threshold']
        pr_thresh = pr_metrics['optimal_threshold']
        if abs(roc_thresh - pr_thresh) < 0.1:
            print("   • ROC and PR optimal thresholds are similar - good sign")
        else:
            print(f"   • ROC optimal: {roc_thresh:.3f}, PR optimal: {pr_thresh:.3f}")
            print("   • Consider your use case: ROC for balanced, PR for imbalanced data")
    
    print("=" * 80)