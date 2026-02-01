---
title: Demand Prediction Service
---

NYC TLC Zones and Routes Management System

# Project Overview

This system provides CRUD operations for managing zones and routes, with parquet file processing capabilities for NYC TLC trip data.

# Setup Instructions

TODO: Add setup instructions in issue #23 (Nico Tov)

# How to Run

## Docker Compose

Build both services using BuildKit for parallel builds:

```bash
COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker compose build
```

Start all services and run in background:

```bash
docker compose up -d
```

View logs:

```bash
docker compose logs -f
```

Stop services:

```bash
docker compose down
```

<details>
<summary>Equivalent manual steps</summary>

Nix devshell provides all dependencies.

## Activate Environment

Start devshell from project root:

```bash
nix develop
```

## Backend Service

Navigate to backend directory:

```bash
cd backend
```

Start FastAPI with uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API available at <http://localhost:8000>

## Frontend Service

Open new terminal in devshell. Navigate to frontend:

```bash
cd frontend
```

Start Streamlit:

```bash
streamlit run app/Home.py --server.port 8501 --server.address 0.0.0.0
```

UI available at <http://localhost:8501>

## Environment Variables

Configure API URL for frontend:

```bash
API_URL=http://localhost:8000 streamlit run app/Home.py
```

</details>

## Endpoints

Backend API runs on <http://localhost:8000>

OpenAPI documentation available at <http://localhost:8000/docs>

Frontend UI runs on <http://localhost:8501>

Health check available at <http://localhost:8000/health>

# API Documentation

Reference `docs/api_contract.md` for complete API documentation.

# Contributing

Reference `CONTRIBUTING.md` for contribution guidelines.
