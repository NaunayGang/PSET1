AGENT CODING GUIDELINES FOR PSET1
==================================

Demand Prediction Service - NYC TLC Zones and Routes Management System with FastAPI
backend, Streamlit frontend, Parquet file processing, and Docker containerization.


BUILD, LINT & TEST COMMANDS
============================

Backend (Python/FastAPI):
  python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
  pytest backend/tests/
  pytest backend/tests/test_zones.py
  pytest backend/tests/test_zones.py::test_create_zone
  pytest backend/tests/ -v
  pytest backend/tests/ --cov=app
  ptw backend/tests/

Frontend (Streamlit):
  streamlit run frontend/app/Home.py

Docker:
  docker-compose up --build
  docker-compose up backend


CODE STYLE GUIDELINES
=====================

Python Standards:
  Version: Python 3.9+
  Formatter: PEP 8 conventions
  Line Length: 88 characters (Black standard)

Imports:
  - Organize in three groups: stdlib, third-party, local (blank lines between)
  - Use absolute imports, not relative
  - Alphabetically sort within groups
  Example:
    import os
    from typing import List, Optional
    
    from fastapi import APIRouter, HTTPException
    from pydantic import BaseModel
    
    from app.schemas import ZoneSchema
    from app.storage import StorageService

Type Hints:
  - Required for all function parameters and return types
  - Use typing module: Optional, List, Dict, Union
  - Use Pydantic models for API schemas in app/schemas.py

Naming Conventions:
  Functions/Variables: snake_case
  Classes: PascalCase
  Constants: UPPER_SNAKE_CASE
  Private members: prefix with _
  File names: snake_case.py (routes: routes_<resource>.py)
  Examples: routes_zones.py, ZoneSchema, create_zone()

Docstrings & Comments:
  - Triple-quoted format for all modules, functions, classes
  - Module docstrings explain purpose and dependencies
  - Function docstrings: description, Args, Returns sections
  - Keep comments minimal, write self-documenting code

Error Handling:
  - Use FastAPI HTTPException for API errors
  - Specify appropriate HTTP status codes
  - Provide meaningful error messages
  - Log errors with context using standard logging

FastAPI Routes:
  - Organize by resource: routes_zones.py, routes_routes.py, routes_uploads.py
  - Each module defines router = APIRouter()
  - Use path parameters for IDs: /zones/{zone_id}
  - Use query parameters for filtering/pagination
  - All endpoints need tags for documentation

Pydantic Models (Schemas):
  - Define in app/schemas.py
  - Use descriptive field names
  - Include Field descriptions for API documentation
  - Use validators for business logic validation

Testing:
  - Test files in backend/tests/ mirroring source structure
  - Name test files: test_<module>.py
  - Name functions: test_<function>_<scenario>()
  - Use pytest fixtures for setup/teardown

Streamlit Frontend:
  - Keep pages in frontend/app/pages/
  - Import API client in each page for backend communication
  - Use descriptive variable names and comments for UI logic
  - Handle API errors gracefully with st.error()


COMMIT STYLE (Angular Convention)
==================================

Prefix: feat, fix, docs, chore, test, refactor
Format: <type>: <imperative-message>
Examples:
  feat: add zones CRUD endpoints
  fix: handle missing zone data in validation
  docs: update API documentation
  test: add test coverage for zone creation

Branch Naming:
  Feature: feature/<issue-description>
  Fix: fix/<issue-description>
  Example: feature/zones-crud-endpoints, fix/validation-error-handling


ARCHITECTURE
============

Backend: FastAPI with async/await support
Frontend: Streamlit for rapid prototyping
Data: Parquet files for NYC TLC trip data
Storage: Modular storage layer (app/storage.py)
Schemas: Pydantic models for validation (app/schemas.py)

Dependencies:
  Backend: FastAPI, Uvicorn, Pydantic, Pandas, PyArrow, Pytest, HTTPx
  Frontend: Streamlit, Requests, Pandas, Plotly
  DevOps: Docker, Docker Compose

Development Environment:
  nix flake update
  nix develop
  Provides: Python 3, Docker, Docker Compose, Pytest
