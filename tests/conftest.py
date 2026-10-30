"""Shared fixtures for API tests."""

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from main import app, storage


@pytest.fixture
def client() -> Iterator[TestClient]:
    storage.clear()
    with TestClient(app) as test_client:
        yield test_client
    storage.clear()


@pytest.fixture
def sample_csv_bytes() -> bytes:
    filepath = Path("fixtures") / "sample_data.csv"
    return filepath.read_bytes()


@pytest.fixture
def uploaded_dataset_id(
    client: TestClient,
    sample_csv_bytes: bytes,
) -> int:
    response = client.post(
        "/upload",
        files={
            "file": (
                "sample_data.csv",
                sample_csv_bytes,
                "text/csv",
            )
        },
    )
    assert response.status_code == 200
    return int(response.json()["id"])


@pytest.fixture
def processing_body() -> dict[str, Any]:
    return {
        "validation": {
            "required_columns": ["student_id", "score"],
            "numeric_columns": ["score"],
        },
        "processing": {
            "remove_duplicates": True,
            "missing": {
                "enabled": True,
                "axis": "rows",
            },
            "outliers": {
                "enabled": False,
                "columns": [],
                "method": "iqr",
                "threshold": 1.5,
            },
        },
    }