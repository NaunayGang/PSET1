# Learning Objectives

-   **Git:** Clear commits, branches, tags.
-   **GitHub:** Issues, PRs, reviews.
-   **Docker:** Reproducible images for backend and frontend.
-   **Docker Compose:** Launch services with correct networking.
-   **FastAPI:** Complete CRUD endpoints (with validations).
-   **Streamlit:** Multipage interface that consumes the backend via HTTP.
-   **Basic Ingestion:** Load a real parquet file and use CRUD endpoints to populate/update data.

# Deliverables

1.  GitHub repository with:
    -   `backend/`, `frontend/`, `docker-compose.yml`
    -   `README.md` (setup, how to run, endpoints, how to use the UI)
    -   `CONTRIBUTING.md` (rules for branches/PR/commits)
    -   `docs/` with decisions + evidence (screenshots, logs)
2.  Services running with Docker Compose:
    -   `api` (FastAPI)
    -   `app` (Streamlit)
3.  Mandatory CRUD of 2 entities: Zones and Routes.
4.  Multipage Streamlit frontend: Home + navigation menu to CRUD pages and Upload.
5.  Parquet loading (NYC TLC): Upload from Streamlit; backend processes create/update Zones and/or Routes via CRUD endpoints.

# Functional Scope (MVP)

Build a Demand Prediction Service with two resources.

## Zone (Mandatory CRUD)

Fields:

-   `id` (int) - TLC LocationID
-   `borough` (string)
-   `zone_name` (string)
-   `service_zone` (string)
-   `active` (bool)
-   `created_at` (datetime)

## Route (Mandatory CRUD)

Fields:

-   `id` (int or uuid)
-   `pickup_zone_id` (int) - reference to `Zone.id`
-   `dropoff_zone_id` (int) - reference to `Zone.id`
-   `name` (string)
-   `active` (bool)
-   `created_at` (datetime)

Minimum rules:

-   `pickup_zone_id` and `dropoff_zone_id` must be > 0
-   `pickup_zone_id` != `dropoff_zone_id` (if equal -> 400)
-   `name` not empty
-   Validate that pickup/dropoff zones exist; otherwise return 400
-   Persistence for PSet #1: in-memory (dict)

# API Specification (FastAPI)

Base URL: `http://localhost:8000`

## Health

-   GET `/health` -> 200 `{ "status": "ok" }`

## CRUD Zones

-   POST `/zones`
-   GET `/zones` (optional filters: active, borough)
-   GET `/zones/{id}`
-   PUT `/zones/{id}`
-   DELETE `/zones/{id}` -> 204

Minimum validation for Zones:

-   `id` positive
-   `zone_name` not empty
-   `borough` not empty

## CRUD Routes

-   POST `/routes`
-   GET `/routes` (optional filters: active, pickup_zone_id, dropoff_zone_id)
-   GET `/routes/{id}`
-   PUT `/routes/{id}`
-   DELETE `/routes/{id}` -> 204

Minimum validation for Routes:

-   `pickup_zone_id`, `dropoff_zone_id` positive
-   `pickup_zone_id` != `dropoff_zone_id` (400 if equal)
-   `name` not empty

## Error Standards

-   400: Business rules / custom validation
-   404: Resource not found
-   422: Automatic Pydantic validation

# Frontend (Streamlit)

Key requirement: Streamlit must consume the backend via HTTP requests; the API URL must be configurable (e.g., `API_URL=http://api:8000` in compose, or `http://localhost:8000` locally).

## Home

-   System title + brief description
-   Backend status (call GET `/health`)
-   Navigation menu to other pages

## Mandatory pages

1.  Zones: List (with filters), create, edit, delete.
2.  Routes: List (with filters), create, edit, delete. Use dropdowns populated from `/zones` for pickup/dropoff.
3.  Load Data: Upload `.parquet`, choose mode (create/update), show summary (# read, created, updated, errors).

Navigation may use Streamlit multipage (`pages/`) or a sidebar menu.

# Load Data

Source: <https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page>

## Objective

Load a real parquet file and, based on the load, create or update resources using the CRUD endpoints for Zones and Routes.

## Upload Endpoint (Backend)

-   Endpoint: POST `/uploads/trips-parquet`
-   Content type: multipart/form-data
-   Parameters:
    -   file: parquet file
    -   mode: "create" or "update"
    -   limit_rows (optional, default: 50_000)
    -   top_n_routes (optional, default: 50)

Response (200):

```json
{
  "file_name": "yellow_tripdata_2024-01.parquet",
  "rows_read": 50000,
  "zones_created": 0,
  "zones_updated": 0,
  "routes_detected": 120,
  "routes_created": 80,
  "routes_updated": 40,
  "errors": []
}
```

## Minimum expected columns

-   `PULocationID`
-   `DOLocationID`

If either column is missing, return 400 with a clear message.

## Minimum logic required

1.  Read parquet using pandas.
2.  Apply `limit_rows` to avoid OOM.
3.  Compute pairs (`PULocationID`, `DOLocationID`) and counts.
4.  Select top N routes by frequency.

For each top route:

-   Create or update via the CRUD endpoints (POST `/routes`, PUT `/routes/{id}`).

Recommended upsert approach:

-   Check existence: GET `/routes?pickup_zone_id=...&dropoff_zone_id=...`.
-   If not exists -> POST `/routes`.
-   If exists -> PUT `/routes/{id}` (e.g., set `active=true` or update `name`).

Zones during load:

-   Create missing Zones found in PULocationID/DOLocationID (POST `/zones` with defaults: borough="Unknown", zone_name="Zone <id>", service_zone="Unknown").
-   Update existing Zones as needed (PUT `/zones/{id}`) e.g., mark `active=true`.

## UI requirements (Upload Parquet)

-   `st.file_uploader` for parquet files.
-   Mode selector (create / update).
-   "Process" button.
-   Summary: rows read, routes detected, created, updated, errors.
-   Show errors in a table or list.

# Docker and Docker Compose

## Services

-   api: Port mapping `8000:8000`, run uvicorn with `--host 0.0.0.0 --port 8000`.
-   app: Port mapping `8501:8501`, run streamlit with `--server.address 0.0.0.0`, depends_on api.

## Technical requirements

-   One Dockerfile per service.
-   `docker-compose.yml` at repo root.
-   Streamlit should call FastAPI via `http://api:8000` when in compose.
-   Include pandas and pyarrow in images for parquet handling.

# Git & GitHub

## Minimum workflow

-   Protect `main` branch (recommended).
-   Branch naming: `feature/...` and `fix/...`.
-   Use PRs for all changes.

## Evidence

-   5+ real Issues.
-   2+ PRs with review/comments.

# Testing

Recommended at least 8 API tests:

-   Zones: create, list, get 404, update, delete.
-   Routes: create, validation pickup==dropoff (400), update 404.
-   Upload: loading parquet returns summary and loaded items appear in list page.

# Repository structure

```
.
├─ backend/
│ ├─ app/
│ │ ├─ main.py
│ │ ├─ routes_zones.py
│ │ ├─ routes_routes.py
│ │ ├─ routes_uploads.py
│ │ ├─ schemas.py
│ │ └─ storage.py
│ ├─ tests/
│ ├─ Dockerfile
│ └─ requirements.txt
├─ frontend/
│ ├─ app/
│ │ ├─ Home.py
│ │ └─ pages/
│ │ ├─ 1_Zones.py
│ │ ├─ 2_Routes.py
│ │ └─ 3_Upload_Parquet.py
│ ├─ Dockerfile
│ └─ requirements.txt
├─ docker-compose.yml
├─ README.md
├─ CONTRIBUTING.md
└─ docs/
    ├─ api_contract.md
    └─ evidence.md
```

# Rubric

-   Git & GitHub (20): issues, PRs, commits, tag.
-   Docker & Compose (25): reproducible build, correct networking.
-   FastAPI CRUD Zones+Routes (30): complete endpoints, validation, errors.
-   Upload Parquet (15): create/update flow with summary.
-   Streamlit UX (10): Home + menu + CRUD pages + error handling.

