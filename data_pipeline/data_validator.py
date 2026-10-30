
"""Validate dataframe columns and numeric values."""

import logging
import pandas as pd

logger = logging.getLogger(__name__)


def validate_dataframe(
    df: pd.DataFrame,
    required_columns: list[str],
    numeric_columns: list[str],
) -> pd.DataFrame:
    """Check required columns and remove invalid numeric rows."""
    before = len(df)
    df = df.copy()

    for col in required_columns:
        if col not in df.columns:
            logger.error("Required column missing: %s", col)
            raise ValueError(f"Required column missing: {col}")

    for col in numeric_columns:
        if col not in df.columns:
            logger.error("Numeric column missing: %s", col)
            raise ValueError(f"Numeric column missing: {col}")

        invalid_rows = []

        for i, value in df[col].items():
            if pd.notna(value):
                try:
                    float(value)
                except (ValueError, TypeError):
                    invalid_rows.append(i)

        if invalid_rows:
            logger.warning(
                "Removing %d rows with invalid numeric values in %s",
                len(invalid_rows),
                col,
            )
            df = df.drop(index=invalid_rows)

        df[col] = pd.to_numeric(df[col])

    logger.debug(
        "Validation completed: %d -> %d rows",
        before,
        len(df),
    )

    return df
