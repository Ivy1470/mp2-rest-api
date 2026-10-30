"""Tests for dataset upload, processing, and retrieval."""

from typing import Any

from fastapi.testclient import TestClient


def test_upload_csv(
    client: TestClient,
    sample_csv_bytes: bytes,
) -> None:
    """Check uploaded dataset metadata."""
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
    result = response.json()
    assert result["rows"] == 6
    assert result["columns"] == 2
    assert isinstance(result["id"], int)
    assert result["id"] > 0


def test_process_and_retrieve(
    client: TestClient,
    uploaded_dataset_id: int,
    processing_body: dict[str, Any],
) -> None:
    """Check cleaning results and stored records."""
    response = client.post(
        f"/datasets/{uploaded_dataset_id}/process",
        json=processing_body,
    )

    assert response.status_code == 200
    result = response.json()
    assert result["id"] == uploaded_dataset_id
    assert result["validation_rows_removed"] == 1
    assert result["cleaning_report"] == {
        "rows_before": 5,
        "rows_after": 3,
        "rows_removed": 2,
        "columns_before": 2,
        "columns_after": 2,
        "columns_removed": 0,
    }

    response = client.get(f"/datasets/{uploaded_dataset_id}")

    assert response.status_code == 200
    result = response.json()
    assert result["total_rows"] == 3
    assert len(result["data"]) == 3

    scores = {
        row["student_id"]: row["score"]
        for row in result["data"]
    }
    assert scores == {1: 80, 2: 90, 5: 85}


def test_retrieve_missing_dataset(client: TestClient) -> None:
    """Check that a missing dataset returns 404."""
    response = client.get("/datasets/999")
    assert response.status_code == 404