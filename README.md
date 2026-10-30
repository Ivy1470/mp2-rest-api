# MP2 Data Processing API

This FastAPI application supports CSV uploads, dataset retrieval, and configurable data processing using reusable modules from MP1. Users can validate required and numeric columns, remove duplicates, handle missing values, and remove outliers. Processing returns a cleaning report and updates the stored dataset after successful validation and processing. The application stores data in memory and logs request IDs, status codes, and response times.

## Run the application

```bash
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Open http://127.0.0.1:8000/docs to try the endpoints.

## Endpoints

- `GET /health`: Check application status.
- `POST /upload`: Upload a CSV file.
- `GET /datasets/{dataset_id}`: Retrieve stored records.
- `POST /datasets/{dataset_id}/process`: Validate and clean a dataset.

## Run tests

```bash
python -m pytest tests -v
```

The three required tests cover CSV upload, processing and retrieval, and retrieval of a missing dataset.