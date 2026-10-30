
"""
Data processing functions for DS3500 MP1.
"""

import logging
from typing import Any
import pandas as pd


logger = logging.getLogger(__name__)


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicate rows from a DataFrame."""
    before = len(df)
    cleaned_df = df.drop_duplicates()
    removed = before - len(cleaned_df)

    logger.debug(
        "remove_duplicates: %d -> %d rows, removed=%d",
        before,
        len(cleaned_df),
        removed
    )
    return cleaned_df



def handle_missing(df: pd.DataFrame, axis: str = "rows") -> pd.DataFrame:
    """Remove rows or columns containing missing values."""
    before = df.shape

    if axis == "rows":
        cleaned_df = df.dropna(axis=0)
    elif axis == "columns":
        cleaned_df = df.dropna(axis=1)
    else:
        logger.error("Invalid axis: %s", axis)
        raise ValueError(f"Invalid axis: {axis}")

    removed = (
        before[0] - cleaned_df.shape[0]
        if axis == "rows"
        else before[1] - cleaned_df.shape[1]
    )

    logger.debug(
        "handle_missing: removed %d %s",
        removed,
        axis
    )

    return cleaned_df



def remove_outliers(
    df: pd.DataFrame,
    columns: list[str],
    method: str = "iqr",
    threshold: float = 1.5
) -> pd.DataFrame:
    """Remove outliers from specified numeric columns."""
    cleaned_df = df.copy()

    if method not in ("iqr", "zscore"):
        logger.error("Unsupported outlier method: %s", method)
        raise ValueError(f"Unsupported outlier method: {method}")

    for column in columns:
        if column not in cleaned_df.columns:
            logger.warning("Column not found: %s", column)
            continue

        if not pd.api.types.is_numeric_dtype(cleaned_df[column]):
            logger.warning("Column is not numeric: %s", column)
            continue

        if method == "iqr":
            q1 = cleaned_df[column].quantile(0.25)
            q3 = cleaned_df[column].quantile(0.75)
            iqr = q3 - q1

            lower = q1 - threshold * iqr
            upper = q3 + threshold * iqr

            cleaned_df = cleaned_df[
                cleaned_df[column].between(lower, upper)
            ]

        elif method == "zscore":
            mean = cleaned_df[column].mean()
            std = cleaned_df[column].std()

            if std == 0 or pd.isna(std):
                continue

            z_scores = (cleaned_df[column] - mean) / std
            cleaned_df = cleaned_df[z_scores.abs() <= threshold]

    logger.debug(
        "remove_outliers: method=%s, threshold=%s, removed=%d rows",
        method,
        threshold,
        len(df) - len(cleaned_df)
    )

    return cleaned_df


def process_data(df: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    """Apply the processing steps enabled in the configuration."""
    settings = config["processing"]
    cleaned_df = df.copy()

    if settings["remove_duplicates"]:
        cleaned_df = remove_duplicates(cleaned_df)

    if settings["missing"]["enabled"]:
        cleaned_df = handle_missing(
            cleaned_df,
            axis=settings["missing"]["axis"]
        )

    if settings["outliers"]["enabled"]:
        outlier_config = settings["outliers"]
        cleaned_df = remove_outliers(
            cleaned_df,
            columns=outlier_config["columns"],
            method=outlier_config["method"],
            threshold=outlier_config["threshold"]
        )

    return cleaned_df



def create_cleaning_report(
    df_before: pd.DataFrame,
    df_after: pd.DataFrame
) -> dict[str, int]:
    """Return a dictionary summarizing the cleaning results."""
    return {
        "rows_before": len(df_before),
        "rows_after": len(df_after),
        "rows_removed": len(df_before) - len(df_after),
        "columns_before": len(df_before.columns),
        "columns_after": len(df_after.columns),
        "columns_removed": len(df_before.columns) - len(df_after.columns)
    }
