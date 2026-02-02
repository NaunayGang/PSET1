---
title: Demand Prediction Service
---

NYC TLC Zones and Routes Management System

# Project Overview

This system provides CRUD operations for managing zones and routes, with parquet file processing capabilities for NYC TLC trip data.

# Prerequisites

- Docker Engine 20.10+
- Docker Compose V2

# Setup Instructions

Clone repository:

```bash
git clone <repository-url>
cd pset1
```

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

## Manual Setup

Nix devshell provides all dependencies.

### Activate Environment

Start devshell from project root:

```bash
nix develop
```

### Backend Service

Navigate to backend directory:

```bash
cd backend
```

Start FastAPI with uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API available at <http://localhost:8000>

### Frontend Service

Open new terminal in devshell. Navigate to frontend:

```bash
cd frontend
```

Start Streamlit:

```bash
streamlit run app/Home.py --server.port 8501 --server.address 0.0.0.0
```

UI available at <http://localhost:8501>

### Environment Variables

Configure API URL for frontend:

```bash
API_URL=http://localhost:8000 streamlit run app/Home.py
```

# Endpoints

Backend API runs on <http://localhost:8000>

OpenAPI documentation available at <http://localhost:8000/docs>

Frontend UI runs on <http://localhost:8501>

Health check available at <http://localhost:8000/health>

# Usage

## Web Interface

Access the Streamlit frontend at <http://localhost:8501>

The interface provides:

- Home page with system overview
- Zones management page for CRUD operations
- Routes management page for CRUD operations
- Upload page for parquet file processing

# API Documentation

Reference `docs/api_contract.md` for complete API documentation.

# Contributing

Reference `CONTRIBUTING.md` for contribution guidelines.


# README checklist

-   [x] `docker compose up --build` starts api and app.
-   [x] Home shows backend health and navigation to pages.
-   [x] CRUD Zones works completely from UI.
-   [x] CRUD Routes works completely from UI (using Zones).
-   [x] Upload parquet processes and performs create/update via CRUD endpoints.
-   [x] README documents how to run and test.
-   [x] Evidence in GitHub (issues/PR/tag) is ready.