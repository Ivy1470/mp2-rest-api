"""
Data loaders for DS3500 MP1.

Supports loading CSV, JSON, and YAML files.
"""

import json
import logging
from pathlib import Path

import pandas as pd
import yaml


logger = logging.getLogger(__name__)


def load_csv(filepath: Path) -> pd.DataFrame:
    """Load a CSV file into a DataFrame."""
    data = pd.read_csv(filepath)
    logger.info("Loaded CSV file: %s (%d rows)", filepath, len(data))
    return data


def load_json(filepath: Path) -> object:
    """Load a JSON file into a Python object."""
    with open(filepath, "r", encoding="utf-8") as file:
        data = json.load(file)

    logger.info("Loaded JSON file: %s", filepath)
    return data


def load_yaml(filepath: Path) -> object:
    """Load a YAML file into a Python object."""
    with open(filepath, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    logger.info("Loaded YAML file: %s", filepath)
    return data


def load_data(filepath: str) -> object:
    """Load a file based on its extension."""
    path = Path(filepath)
    extension = path.suffix.lower()

    if extension == ".csv":
        return load_csv(path)
    elif extension == ".json":
        return load_json(path)
    elif extension == ".yaml":
        return load_yaml(path)
    else:
        logger.error("Unsupported file format: %s", extension)
        raise ValueError(f"Unsupported file format: {extension}")
