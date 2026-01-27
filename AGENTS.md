AGENT CODING GUIDELINES FOR PSET1
==================================

Demand Prediction Service - NYC TLC Zones and Routes Management System with FastAPI
backend, Streamlit frontend, Parquet file processing, and Docker containerization.


BUILD, LINT & TEST COMMANDS
============================

Backend: python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
         pytest backend/tests/ (all) or pytest backend/tests/test_zones.py (single file)
         pytest backend/tests/test_zones.py::test_create_zone (single test)

Frontend: streamlit run frontend/app/Home.py

Docker: docker-compose up --build


CODE STYLE GUIDELINES
=====================

Python Standards: Python 3.9+, PEP 8, 88 character line length

Imports: Three groups (stdlib, third-party, local) with blank line separators.
  Absolute imports, alphabetically sorted within groups.
  import os / from typing import List / from fastapi import APIRouter / from app.schemas import ZoneSchema

Type Hints: Required for all function parameters and return types.
  Use Optional, List, Dict, Union from typing module.
  Use Pydantic models in app/schemas.py for API schemas.

Naming: Functions/vars snake_case, Classes PascalCase, Constants UPPER_SNAKE_CASE.
  Private members prefix with _. Files snake_case.py, routes routes_<resource>.py.
  Examples: create_zone(), ZoneSchema, routes_zones.py

Docstrings: Triple-quoted format for modules, functions, classes.
  Module docstrings explain purpose/dependencies.
  Function docstrings: description, Args, Returns sections.
  Minimal comments, write self-documenting code.

Error Handling: Use FastAPI HTTPException with appropriate status codes.
  Provide meaningful error messages.
  Log errors with context using standard logging.

FastAPI Routes: Organize by resource (routes_zones.py, routes_routes.py, routes_uploads.py).
  Each module defines router = APIRouter().
  Use path parameters for IDs: /zones/{zone_id}
  Use query parameters for filtering/pagination.
  All endpoints need tags for documentation.

Pydantic Models: Define in app/schemas.py.
  Use descriptive field names with Field descriptions for API docs.
  Use validators for business logic validation.

Testing: Test files in backend/tests/ mirroring source structure.
  Name files test_<module>.py, functions test_<function>_<scenario>().
  Use pytest fixtures for setup/teardown.

Streamlit: Keep pages in frontend/app/pages/.
  Import API client in each page.
  Handle API errors gracefully with st.error().


COMMIT STYLE (Angular Convention)
==================================

Prefix: feat, fix, docs, chore, test, refactor
Format: <type>: <imperative-message>
Examples: feat: add zones CRUD endpoints / fix: handle missing zone data

Branches: feature/<issue-description> or fix/<issue-description>


ARCHITECTURE
============

Backend: FastAPI with async/await
Frontend: Streamlit for prototyping
Data: Parquet files for NYC TLC trip data
Storage: Modular layer (app/storage.py)
Schemas: Pydantic models (app/schemas.py)

Dependencies: FastAPI, Uvicorn, Pydantic, Pandas, PyArrow, Pytest, HTTPx (backend)
             Streamlit, Requests, Pandas, Plotly (frontend)
             Docker, Docker Compose (devops)

Dev Environment: nix develop
