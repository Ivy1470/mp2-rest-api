import logging
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


class DatasetStorage:
    def __init__(self) -> None:
        self._store: dict[int, dict[str, Any]] = {}
        self._counter: int = 0

    def save(self, df: pd.DataFrame, filename: str) -> int:
        """Store a copy of the data and return a new integer ID."""
        self._counter += 1
        dataset_id = self._counter

        self._store[dataset_id] = {
            "filename": filename,
            "df": df.copy()
        }

        logger.debug(
            "Stored dataset: id=%s, rows=%s",
            dataset_id,
            len(df)
        )

        return dataset_id

    
    def get(self, dataset_id: int) -> pd.DataFrame | None:
        """Return a copy of the stored DataFrame, or None."""
        dataset = self._store.get(dataset_id)

        if dataset is None:
            logger.debug("Dataset not found: id=%s", dataset_id)
            return None

        df: pd.DataFrame = dataset["df"]

        logger.debug(
            "Retrieved dataset copy: id=%s, rows=%s",
            dataset_id,
            len(df)
        )

        return df.copy()


    def get_metadata(self, dataset_id: int) -> dict[str, Any] | None:
        """Return the dataset metadata, or None."""
        dataset = self._store.get(dataset_id)

        if dataset is None:
            logger.debug("Metadata not found: id=%s", dataset_id)
            return None

        df: pd.DataFrame = dataset["df"]

        metadata = {
            "id": dataset_id,
            "filename": dataset["filename"],
            "rows": df.shape[0],
            "columns": df.shape[1],
            "column_names": df.columns.tolist()
        }

        logger.debug("Retrieved dataset metadata: id=%s", dataset_id)

        return metadata


    def update(self, dataset_id: int, df: pd.DataFrame) -> bool:
        """Replace an existing dataset; return False if missing."""
        if dataset_id not in self._store:
            logger.debug("Update failed: dataset not found, id=%s", dataset_id)
            return False

        self._store[dataset_id]["df"] = df.copy()

        logger.debug(
            "Updated dataset: id=%s, rows=%s",
            dataset_id,
            len(df)
        )

        return True

    def clear(self) -> None:
        """Clear all data and reset the ID counter."""
        self._store.clear()
        self._counter = 0

        logger.debug("Cleared all datasets and reset ID counter")