# Agent Coding Guidelines for PSET1

This guide is designed for agentic coding tools (like OpenCode, Copilot, or Cursor) to understand and work effectively in this repository.

## Project Overview

**Demand Prediction Service** - A NYC TLC Zones and Routes Management System with:
- FastAPI backend (Python) for CRUD operations and data processing
- Streamlit frontend for visualization and management
- Parquet file processing for NYC TLC trip data
- Docker containerization

## Build, Lint & Test Commands

### Backend (Python/FastAPI)

```bash
# Run the API server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run all tests
pytest backend/tests/

# Run a single test file
pytest backend/tests/test_zones.py

# Run a single test
pytest backend/tests/test_zones.py::test_create_zone

# Run tests with verbose output
pytest backend/tests/ -v

# Run tests with coverage
pytest backend/tests/ --cov=app

# Run tests in watch mode (requires pytest-watch)
ptw backend/tests/
```

### Frontend (Streamlit)

```bash
# Run the Streamlit app
streamlit run frontend/app/Home.py
```

### Docker

```bash
# Build and run all services
docker-compose up --build

# Run specific service
docker-compose up backend
```

## Code Style Guidelines

### General Python Standards

- **Python Version**: Python 3.9+
- **Code Formatter**: Follow PEP 8 conventions (no automatic formatter configured yet)
- **Line Length**: Aim for 88 characters (Black standard)

### Imports

- Organize in three groups: stdlib, third-party, local (with blank lines between)
- Use absolute imports, not relative imports
- Import statements should be alphabetically sorted within groups
- Example:
  ```python
  import os
  from typing import List, Optional
  
  from fastapi import APIRouter, HTTPException
  from pydantic import BaseModel
  
  from app.schemas import ZoneSchema
  from app.storage import StorageService
  ```

### Type Hints

- **Required** for all function parameters and return types
- Use typing module for complex types: `Optional`, `List`, `Dict`, `Union`
- Use Pydantic models for API schemas (models in `app/schemas.py`)
- Example:
  ```python
  def create_zone(zone_data: ZoneSchema) -> Dict[str, Any]:
      """Create a new zone."""
      pass
  ```

### Naming Conventions

- **Functions/Variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private members**: prefix with `_` (e.g., `_internal_method`)
- **File names**: `snake_case.py` (except routes: `routes_<resource>.py`)
- Examples:
  - Module: `routes_zones.py`, `schemas.py`, `storage.py`
  - Classes: `ZoneSchema`, `RouteHandler`, `StorageService`
  - Functions: `create_zone()`, `validate_data()`

### Docstrings & Comments

- Use triple-quoted docstring format for all modules, functions, and classes
- Module docstrings at the top explain purpose and dependencies
- Function docstrings include description, Args, Returns sections
- Keep comments minimal; write self-documenting code
- Example:
  ```python
  """
  Zones CRUD endpoints.
  
  This module implements all CRUD operations for Zone resources:
  - POST /zones - Create a new zone
  - GET /zones - List all zones (with optional filters)
  """
  
  def create_zone(zone_data: ZoneSchema) -> ZoneSchema:
      """
      Create a new zone.
      
      Args:
          zone_data: Zone data to create
          
      Returns:
          Created zone object
          
      Raises:
          HTTPException: If zone already exists
      """
  ```

### Error Handling

- Use FastAPI's `HTTPException` for API errors
- Specify appropriate HTTP status codes (400, 404, 500, etc.)
- Provide meaningful error messages
- Log errors with context (use standard logging module)
- Example:
  ```python
  from fastapi import HTTPException, status
  
  if not zone_exists:
      raise HTTPException(
          status_code=status.HTTP_404_NOT_FOUND,
          detail=f"Zone with id {zone_id} not found"
      )
  ```

### FastAPI Routes

- Organize routes by resource: `routes_zones.py`, `routes_routes.py`, `routes_uploads.py`
- Each module should define a `router = APIRouter()` object
- Use path parameters for IDs: `/zones/{zone_id}`
- Use query parameters for filtering/pagination
- All endpoints need `tags` for documentation
- Example:
  ```python
  @router.get("/zones/{zone_id}", tags=["Zones"])
  async def get_zone(zone_id: int) -> ZoneSchema:
      """Get a specific zone by ID."""
  ```

### Pydantic Models (Schemas)

- Define in `app/schemas.py`
- Use descriptive field names
- Include Field descriptions for API documentation
- Use validators for business logic validation
- Example:
  ```python
  from pydantic import BaseModel, Field
  
  class ZoneSchema(BaseModel):
      name: str = Field(..., description="Unique zone name")
      district_id: int = Field(..., ge=1, description="NYC district ID")
  ```

### Testing

- Test files in `backend/tests/` mirroring source structure
- Name test files: `test_<module>.py`
- Name test functions: `test_<function>_<scenario>()`
- Use pytest fixtures for setup/teardown
- Example:
  ```python
  def test_create_zone_success():
      """Test successful zone creation."""
      result = create_zone(valid_data)
      assert result.id is not None
  ```

### Streamlit Frontend

- Keep pages in `frontend/app/pages/`
- Import API client in each page for backend communication
- Use descriptive variable names and comments for UI logic
- Handle API errors gracefully with `st.error()`

## Commit Style (Angular Convention)

Following the project's Angular commit style:

- **Prefix**: `feat`, `fix`, `docs`, `chore`, `test`, `refactor`
- **Format**: `<type>: <imperative-message>`
- **Examples**:
  - `feat: add zones CRUD endpoints`
  - `fix: handle missing zone data in validation`
  - `docs: update API documentation`
  - `test: add test coverage for zone creation`

## Branch Naming

- Feature branches: `feature/<issue-description>`
- Fix branches: `fix/<issue-description>`
- Example: `feature/zones-crud-endpoints`, `fix/validation-error-handling`

## Architecture Notes

- **Backend**: FastAPI with async/await support
- **Frontend**: Streamlit for rapid prototyping
- **Data**: Parquet files for NYC TLC trip data
- **Storage**: Modular storage layer (`app/storage.py`)
- **Schemas**: Pydantic models for validation (`app/schemas.py`)

## Dependencies

- **Backend**: FastAPI, Uvicorn, Pydantic, Pandas, PyArrow, Pytest, HTTPx
- **Frontend**: Streamlit, Requests, Pandas, Plotly
- **DevOps**: Docker, Docker Compose

## Development Environment

Use Nix flake for reproducible environment:
```bash
nix flake update
nix develop
```

This provides Python 3, Docker, Docker Compose, Pytest, and other tools.

