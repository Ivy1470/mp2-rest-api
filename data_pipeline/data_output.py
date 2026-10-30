
"""Save processed data to CSV files."""

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def save_data(df: pd.DataFrame, filepath: str) -> Path:
    """Save a dataframe to a CSV file."""
    path = Path(filepath)

    path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(path, index=False)

    logger.debug(
        "Saved %d rows to %s",
        len(df),
        path,
    )

    return path
