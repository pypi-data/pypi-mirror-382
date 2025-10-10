"""
Internal validation utilities for input checking.

This module provides shared validation functions to reduce code duplication
across the package and ensure consistent input validation.
"""

import numpy as np
import pandas as pd
from typing import Union, Tuple


def validate_estimator(model) -> None:
    """
    Validate that model has required sklearn methods.

    Parameters
    ----------
    model : object
        The model to validate

    Raises
    ------
    ValueError
        If model doesn't have required methods
    """
    if not hasattr(model, "fit") or not hasattr(model, "predict"):
        raise ValueError(
            "Model must have 'fit' and 'predict' methods (sklearn-compatible estimator)"
        )


def validate_input_arrays(
    X: Union[pd.DataFrame, np.ndarray], y: Union[pd.Series, np.ndarray]
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Validate and convert input arrays.

    Parameters
    ----------
    X : array-like of shape (n_samples, n_features)
        Feature data
    y : array-like of shape (n_samples,)
        Target values

    Returns
    -------
    X_array, y_array : tuple of np.ndarray
        Validated arrays

    Raises
    ------
    ValueError
        If arrays are empty, have wrong dimensions, or incompatible lengths
    """
    X_array = np.asarray(X)
    y_array = np.asarray(y)

    # Validate X
    if X_array.size == 0:
        raise ValueError("X cannot be empty")
    if X_array.ndim != 2:
        raise ValueError(f"X must be 2-dimensional, got {X_array.ndim} dimensions")

    # Validate y
    if y_array.size == 0:
        raise ValueError("y cannot be empty")
    if y_array.ndim != 1:
        raise ValueError(f"y must be 1-dimensional, got {y_array.ndim} dimensions")

    # Check length compatibility
    if len(X_array) != len(y_array):
        raise ValueError(
            f"X and y must have same number of samples. "
            f"X: {len(X_array)}, y: {len(y_array)}"
        )

    return X_array, y_array


def validate_no_nan_inf(
    X: Union[pd.DataFrame, np.ndarray],
    X_array: np.ndarray,
    y_array: np.ndarray,
    check_y_numeric: bool = True,
) -> None:
    """
    Check for NaN/inf values in arrays.

    Parameters
    ----------
    X : array-like
        Original X data (used for DataFrame type checking)
    X_array : np.ndarray
        Numpy array version of X
    y_array : np.ndarray
        Numpy array version of y
    check_y_numeric : bool, default=True
        If True, check for numeric NaN/inf. If False, only check for NaN.

    Raises
    ------
    ValueError
        If NaN or infinite values are found
    """
    # Check y
    if check_y_numeric:
        if np.any(np.isnan(y_array)) or np.any(np.isinf(y_array)):
            raise ValueError("y contains NaN or infinite values")
    else:
        if np.any(pd.isnull(y_array)):
            raise ValueError("y contains NaN values")

    # Check X (handle mixed data types)
    try:
        if X_array.dtype.kind in ["i", "f"]:  # integer or float
            if np.any(np.isnan(X_array)) or np.any(np.isinf(X_array)):
                raise ValueError("X contains NaN or infinite values")
        elif isinstance(X, pd.DataFrame):
            # For DataFrames, check only numeric columns
            numeric_cols = X.select_dtypes(include=[np.number])
            if len(numeric_cols.columns) > 0:
                if (
                    numeric_cols.isnull().any().any()
                    or np.isinf(numeric_cols.values).any()
                ):
                    raise ValueError("X contains NaN or infinite values")
    except (TypeError, ValueError) as e:
        if "NaN or infinite values" in str(e):
            raise e
        # If we can't check (e.g., object arrays with mixed types), skip validation
        # The sklearn estimator will handle invalid data during fitting
        pass


def validate_cv_parameter(cv: int, n_samples: int) -> None:
    """
    Validate cross-validation parameter.

    Parameters
    ----------
    cv : int
        Number of cross-validation folds
    n_samples : int
        Number of samples in dataset

    Raises
    ------
    ValueError
        If cv is invalid
    """
    if not isinstance(cv, int) or cv < 2:
        raise ValueError(f"cv must be an integer >= 2, got {cv}")
    if cv > n_samples:
        raise ValueError(
            f"cv ({cv}) cannot be greater than number of samples ({n_samples})"
        )


def validate_sklearn_inputs(
    model,
    X: Union[pd.DataFrame, np.ndarray],
    y: Union[pd.Series, np.ndarray],
    cv: int,
    check_y_numeric: bool = True,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Complete validation pipeline for sklearn-style inputs.

    This convenience function combines all validation steps:
    - Estimator validation
    - Array shape and size validation
    - NaN/inf checking
    - Cross-validation parameter validation

    Parameters
    ----------
    model : object
        The sklearn-compatible model
    X : array-like of shape (n_samples, n_features)
        Feature data
    y : array-like of shape (n_samples,)
        Target values
    cv : int
        Number of cross-validation folds
    check_y_numeric : bool, default=True
        If True, check for numeric NaN/inf in y. If False, only check for NaN.
        Use False for classification tasks with non-numeric labels.

    Returns
    -------
    X_array, y_array : tuple of np.ndarray
        Validated arrays

    Raises
    ------
    ValueError
        If any validation check fails

    Examples
    --------
    >>> from sklearn.linear_model import LinearRegression
    >>> model = LinearRegression()
    >>> X = [[1, 2], [3, 4], [5, 6]]
    >>> y = [1, 2, 3]
    >>> X_val, y_val = validate_sklearn_inputs(model, X, y, cv=2)
    >>> X_val.shape
    (3, 2)
    """
    validate_estimator(model)
    X_array, y_array = validate_input_arrays(X, y)
    validate_no_nan_inf(X, X_array, y_array, check_y_numeric)
    validate_cv_parameter(cv, len(y_array))
    return X_array, y_array
