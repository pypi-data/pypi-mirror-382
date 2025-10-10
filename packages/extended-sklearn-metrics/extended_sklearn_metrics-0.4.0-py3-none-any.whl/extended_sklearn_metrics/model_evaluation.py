import numpy as np
import pandas as pd
from sklearn.model_selection import cross_validate
from sklearn.base import is_regressor
from typing import Union, Dict, Any, Optional, Protocol, Tuple
import warnings

from ._validation import validate_sklearn_inputs


class CustomThresholds:
    """Class to define custom performance thresholds"""

    def __init__(
        self,
        error_thresholds: Tuple[float, float, float] = (10, 20, 30),
        score_thresholds: Tuple[float, float] = (0.5, 0.7),
    ):
        """
        Parameters
        ----------
        error_thresholds : tuple of 3 floats
            Thresholds for error metrics (RMSE, MAE) as percentages.
            Format: (excellent_threshold, good_threshold, moderate_threshold)
            Values above moderate_threshold are considered "Poor"
        score_thresholds : tuple of 2 floats
            Thresholds for score metrics (R², Explained Variance).
            Format: (poor_threshold, good_threshold)
            Scores below poor_threshold are "Poor", above good_threshold are "Good"
        """
        self.error_thresholds = error_thresholds
        self.score_thresholds = score_thresholds


class SklearnEstimator(Protocol):
    """Protocol for sklearn-compatible estimators."""

    def fit(
        self, X: Union[pd.DataFrame, np.ndarray], y: Union[pd.Series, np.ndarray]
    ) -> "SklearnEstimator": ...

    def predict(self, X: Union[pd.DataFrame, np.ndarray]) -> np.ndarray: ...


def evaluate_model_with_cross_validation(
    model: SklearnEstimator,
    X: Union[pd.DataFrame, np.ndarray],
    y: Union[pd.Series, np.ndarray],
    cv: int = 5,
    target_range: Optional[float] = None,
    custom_thresholds: Optional[CustomThresholds] = None,
) -> pd.DataFrame:
    """
    Evaluates a regression model using cross-validation and generates a performance summary table.

    Parameters
    ----------
    model : estimator object
        The machine learning model to evaluate (must implement fit and predict).
    X : array-like of shape (n_samples, n_features)
        Training data.
    y : array-like of shape (n_samples,)
        Target values.
    cv : int, default=5
        Number of cross-validation folds.
    target_range : float, optional
        The range of the target variable (max(y) - min(y)). Required for RMSE and MAE percentage calculations.
    custom_thresholds : CustomThresholds, optional
        Custom thresholds for performance evaluation. If None, uses default thresholds.

    Returns
    -------
    pd.DataFrame
        A summary table containing performance metrics and their interpretations.
    """
    # Input validation using shared validation utilities
    X_array, y_array = validate_sklearn_inputs(model, X, y, cv, check_y_numeric=True)

    # Validate target_range
    if target_range is not None:
        if not isinstance(target_range, (int, float)) or target_range <= 0:
            raise ValueError(
                f"target_range must be a positive number, got {target_range}"
            )

    # Calculate target_range if not provided
    if target_range is None:
        target_range = np.max(y_array) - np.min(y_array)
        if target_range == 0:
            warnings.warn(
                "Target variable has zero variance. Percentage calculations may not be meaningful.",
                UserWarning,
            )
            target_range = 1  # Avoid division by zero

    # Check if model appears to be for regression
    if hasattr(model, "_estimator_type"):
        if model._estimator_type != "regressor":
            warnings.warn(
                f"Model appears to be a '{model._estimator_type}', but this function is designed for regression models.",
                UserWarning,
            )

    # Define scoring metrics
    scoring = {
        "neg_root_mean_squared_error": "neg_root_mean_squared_error",
        "neg_mean_absolute_error": "neg_mean_absolute_error",
        "r2": "r2",
        "explained_variance": "explained_variance",
    }

    # Perform cross-validation
    cv_results = cross_validate(
        model, X, y, cv=cv, scoring=scoring, return_train_score=False
    )

    # Calculate mean scores
    rmse = -np.mean(cv_results["test_neg_root_mean_squared_error"])
    mae = -np.mean(cv_results["test_neg_mean_absolute_error"])
    r2 = np.mean(cv_results["test_r2"])
    exp_var = np.mean(cv_results["test_explained_variance"])

    # Calculate error percentages
    rmse_percentage = (rmse / target_range) * 100
    mae_percentage = (mae / target_range) * 100

    # Use custom thresholds if provided, otherwise use defaults
    if custom_thresholds is None:
        custom_thresholds = CustomThresholds()

    # Define performance categories using custom thresholds
    def get_error_performance(error_percentage: float) -> str:
        exc_thresh, good_thresh, mod_thresh = custom_thresholds.error_thresholds
        if error_percentage < exc_thresh:
            return "Excellent"
        elif error_percentage < good_thresh:
            return "Good"
        elif error_percentage < mod_thresh:
            return "Moderate"
        else:
            return "Poor"

    def get_score_performance(score: float) -> str:
        poor_thresh, good_thresh = custom_thresholds.score_thresholds
        if score > good_thresh:
            return "Good"
        elif score > poor_thresh:
            return "Acceptable"
        else:
            return "Poor"

    # Create results DataFrame
    results = pd.DataFrame(
        {
            "Metric": ["RMSE", "MAE", "R²", "Explained Variance"],
            "Value": [rmse, mae, r2, exp_var],
            "Threshold": [
                f"<{custom_thresholds.error_thresholds[0]}% = Excellent, {custom_thresholds.error_thresholds[0]}-{custom_thresholds.error_thresholds[1]}% = Good, {custom_thresholds.error_thresholds[1]}-{custom_thresholds.error_thresholds[2]}% = Moderate, >{custom_thresholds.error_thresholds[2]}% = Poor",
                f"<{custom_thresholds.error_thresholds[0]}% = Excellent, {custom_thresholds.error_thresholds[0]}-{custom_thresholds.error_thresholds[1]}% = Good, {custom_thresholds.error_thresholds[1]}-{custom_thresholds.error_thresholds[2]}% = Moderate, >{custom_thresholds.error_thresholds[2]}% = Poor",
                f"> {custom_thresholds.score_thresholds[1]} = Good, {custom_thresholds.score_thresholds[0]}–{custom_thresholds.score_thresholds[1]} = Acceptable, < {custom_thresholds.score_thresholds[0]} = Poor",
                f"> {custom_thresholds.score_thresholds[1]} = Good, {custom_thresholds.score_thresholds[0]}–{custom_thresholds.score_thresholds[1]} = Acceptable, < {custom_thresholds.score_thresholds[0]} = Poor",
            ],
            "Calculation": [
                f"{rmse:.4f} / {target_range:.2f} * 100 ≈ {rmse_percentage:.2f}%",
                f"{mae:.4f} / {target_range:.2f} * 100 ≈ {mae_percentage:.2f}%",
                "N/A (unitless)",
                "N/A (unitless)",
            ],
            "Performance": [
                get_error_performance(rmse_percentage),
                get_error_performance(mae_percentage),
                get_score_performance(r2),
                get_score_performance(exp_var),
            ],
        }
    )

    return results
