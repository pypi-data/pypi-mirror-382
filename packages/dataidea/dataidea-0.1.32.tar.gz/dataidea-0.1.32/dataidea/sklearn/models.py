"""
Functions for saving and loading machine learning models
"""

from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score, 
    classification_report as sklearn_classification_report)
import numpy as np
import pandas as pd


def regression_report(y_true, y_pred, n_features=None, output_dict=False, index_name='Metric'):
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    n = y_true.shape[0]

    r2 = r2_score(y_true, y_pred)
    adjusted_r2 = None
    if n_features is not None:
        denom = (n - n_features - 1)
        adjusted_r2 = 1 - ((1 - r2) * (n - 1) / denom) if denom > 0 else np.nan

    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)                         # <-- do this instead of squared=False
    mae = mean_absolute_error(y_true, y_pred)

    corr = np.corrcoef(y_true, y_pred)[0, 1]
    if not np.isfinite(corr):
        corr = np.nan

    report = {
        'MSE': mse,
        'RMSE': rmse,
        'MAE': mae,
        'R2': r2,
        'Adjusted R2': adjusted_r2,
        'Correlation': corr
    }

    if output_dict:
        return report
    else:
        df = pd.DataFrame.from_dict(report, orient='index', columns=['Value'])
        df.index.name = index_name
        return df


def classification_report(y_true, y_pred, output_dict=False):
    """
    Generate a classification report for the model.
    
    Parameters:
    -----------
    y_true : array-like
        The true labels
    y_pred : array-like
        The predicted labels
    average : str, default='binary'
        The average method to use for the classification report
    output_dict : bool, default=False
        Whether to return the report as a dictionary or a string
    """
    return sklearn_classification_report(y_true, y_pred, output_dict=output_dict)

__all__ = ['regression_report', 'classification_report'] 