import io
import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile

from src import (
    DatasetInfo,
    DatasetStorage,
    HealthResponse,
    ProcessConfig,
    ProcessingReport,
    setup_logging,
    log_requests,
)
from data_pipeline import (
    create_cleaning_report,
    process_data,
    validate_dataframe,
)

setup_logging(verbose=True)
logger = logging.getLogger(__name__)

app = FastAPI(title="Data Processing API", version="1.0.0")
app.middleware("http")(log_requests)
storage = DatasetStorage()


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return the application status and version."""
    return HealthResponse(status="ok", version="1.0.0")


@app.post("/upload", response_model=DatasetInfo)
async def upload_dataset(file: UploadFile = File(...)) -> DatasetInfo:
    """Read and store a CSV upload."""
    filename = file.filename or ""
    extension = Path(filename).suffix.lower()

    if extension != ".csv":
        logger.warning("Unsupported file format: %s", extension)
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported."
        )

    contents = await file.read()

    try:
        df = pd.read_csv(io.BytesIO(contents))
    except (
        pd.errors.EmptyDataError,
        pd.errors.ParserError,
        UnicodeDecodeError
    ) as exc:
        logger.warning("Unable to read CSV: %s", exc)
        raise HTTPException(
            status_code=400,
            detail="Unable to read CSV. Check the file format and encoding."
        ) from exc

    dataset_id = storage.save(df, filename)
    metadata = storage.get_metadata(dataset_id)

    if metadata is None:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve saved dataset metadata."
        )

    logger.info(
        "Uploaded dataset: id=%s, filename=%s, rows=%s",
        dataset_id,
        filename,
        len(df)
    )

    return DatasetInfo(**metadata)

@app.get("/datasets/{dataset_id}")
def get_dataset(
    dataset_id: int,
    limit: int = Query(default=100, ge=1)
) -> dict[str, Any]:
    """Return up to limit rows from a stored dataset."""
    df = storage.get(dataset_id)

    if df is None:
        logger.warning("Dataset not found: %s", dataset_id)
        raise HTTPException(
            status_code=404,
            detail="Dataset not found."
        )

    records = json.loads(df.head(limit).to_json(orient="records"))

    logger.info(
        "Retrieved dataset: id=%s, returned_rows=%s",
        dataset_id,
        len(records)
    )

    return {
        "id": dataset_id,
        "data": records,
        "total_rows": len(df)
    }

@app.post(
    "/datasets/{dataset_id}/process",
    response_model=ProcessingReport,
)
def process_dataset(
    dataset_id: int,
    config: ProcessConfig,
) -> dict[str, Any]:
    """Validate and process a stored dataset."""
    df = storage.get(dataset_id)

    if df is None:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    config_dict = config.model_dump()

    try:
        for column in config.validation.numeric_columns:
            if column not in df.columns:
                raise ValueError(f"Numeric column missing: {column}")

        validated_df = validate_dataframe(
            df,
            required_columns=config.validation.required_columns,
            numeric_columns=config.validation.numeric_columns,
        )
        validation_rows_removed = len(df) - len(validated_df)

        logger.info(
            "Validated dataset: id=%s, rows_removed=%s",
            dataset_id,
            validation_rows_removed,
        )

        before_processing = validated_df.copy()
        processed_df = process_data(validated_df, config_dict)
        cleaning_report = create_cleaning_report(
            before_processing,
            processed_df,
        )

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    storage.update(dataset_id, processed_df)

    logger.info(
        "Processed dataset: id=%s, rows_before=%s, rows_after=%s",
        dataset_id,
        cleaning_report["rows_before"],
        cleaning_report["rows_after"],
    )

    return {
        "id": dataset_id,
        "validation_rows_removed": validation_rows_removed,
        "cleaning_report": cleaning_report,
    }