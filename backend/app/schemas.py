"""
Pydantic schemas for API request/response models.

These schemas define the API contract between frontend and backend,
enabling parallel development with type safety and validation.
FastAPI will auto-generate OpenAPI/Swagger spec from these models.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


# =============================================================================
# Zone Schemas
# =============================================================================
# Zones represent NYC TLC Location IDs with geographic information.
# Used for CRUD operations: Create, Read, Update, Delete zones via API.
#
# Schema pattern:
# - ZoneBase: Common fields shared by all zone operations
# - ZoneCreate: For POST /zones (creating new zones)
# - ZoneUpdate: For PUT /zones/{id} (updating existing zones)
# - ZoneResponse: For GET /zones (what API returns to frontend)

class ZoneBase(BaseModel):
    """Base schema for Zone with common fields."""

    id: int = Field(..., gt=0, description="TLC LocationID, must be positive")
    borough: str = Field(..., min_length=1, description="Borough name, not empty")
    zone_name: str = Field(..., min_length=1, description="Zone name, not empty")
    service_zone: str = Field(..., description="Service zone designation")
    active: bool = Field(default=True, description="Whether zone is active")

    @field_validator('borough', 'zone_name')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Ensure string fields are not empty or whitespace-only."""
        if not v or not v.strip():
            raise ValueError('Field cannot be empty or whitespace-only')
        return v.strip()


class ZoneCreate(ZoneBase):
    """Schema for creating a new Zone."""
    # 'pass' means: inherit everything from ZoneBase without modifications.
    # We create separate classes for semantic clarity (ZoneCreate vs ZoneUpdate)
    # and future flexibility (easy to add create-specific validation later).
    pass


class ZoneUpdate(ZoneBase):
    """Schema for updating an existing Zone."""
    pass


class ZoneResponse(ZoneBase):
    """Schema for Zone response with auto-generated fields."""

    created_at: datetime = Field(..., description="Timestamp of creation")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "borough": "Manhattan",
                "zone_name": "Newark Airport",
                "service_zone": "EWR",
                "active": True,
                "created_at": "2025-01-25T20:00:00Z"
            }
        }


# =============================================================================
# Route Schemas
# =============================================================================
# Routes represent pickup-dropoff zone pairs (e.g., "Manhattan to JFK").
# Used to track popular taxi routes based on trip data analysis.
#
# Schema pattern:
# - RouteBase: Common fields (pickup_zone_id, dropoff_zone_id, name, active)
# - RouteCreate: For POST /routes (creating new routes)
# - RouteUpdate: For PUT /routes/{id} (updating existing routes)
# - RouteResponse: For GET /routes (includes auto-generated id and created_at)
#
# Key validation: pickup_zone_id must != dropoff_zone_id (can't route to same zone)

class RouteBase(BaseModel):
    """Base schema for Route with common fields."""

    pickup_zone_id: int = Field(..., gt=0, description="Pickup zone ID, must be positive")
    dropoff_zone_id: int = Field(..., gt=0, description="Dropoff zone ID, must be positive")
    name: str = Field(..., min_length=1, description="Route name, not empty")
    active: bool = Field(default=True, description="Whether route is active")

    @field_validator('name')
    @classmethod
    def validate_name_not_empty(cls, v: str) -> str:
        """Ensure name is not empty or whitespace-only."""
        if not v or not v.strip():
            raise ValueError('Route name cannot be empty or whitespace-only')
        return v.strip()

    @field_validator('dropoff_zone_id')
    @classmethod
    def validate_different_zones(cls, v: int, info) -> int:
        """Ensure pickup and dropoff zones are different."""
        if 'pickup_zone_id' in info.data and v == info.data['pickup_zone_id']:
            raise ValueError('pickup_zone_id and dropoff_zone_id must be different')
        return v


class RouteCreate(RouteBase):
    """Schema for creating a new Route."""
    pass


class RouteUpdate(RouteBase):
    """Schema for updating an existing Route."""
    pass


class RouteResponse(RouteBase):
    """Schema for Route response with auto-generated fields."""

    id: int = Field(..., description="Route identifier")
    created_at: datetime = Field(..., description="Timestamp of creation")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "pickup_zone_id": 1,
                "dropoff_zone_id": 2,
                "name": "Manhattan to JFK",
                "active": True,
                "created_at": "2025-01-25T20:10:00Z"
            }
        }


# =============================================================================
# Upload Schemas
# =============================================================================
# Upload schemas handle parquet file processing for NYC TLC trip data.
# Process parquet → extract (PULocationID, DOLocationID) pairs → create/update zones & routes.
#
# Schemas:
# - UploadMode: Input parameters (mode: create/update, limit_rows, top_n_routes)
# - UploadResponse: Processing summary (rows read, zones/routes created/updated, errors)
#
# Usage: Frontend uploads .parquet → Backend processes → Returns UploadResponse

class UploadMode(BaseModel):
    """Schema for upload processing mode."""

    mode: str = Field(..., pattern="^(create|update)$", description="Processing mode")
    limit_rows: int = Field(default=50000, gt=0, le=1000000, description="Maximum rows to process")
    top_n_routes: int = Field(default=50, gt=0, le=500, description="Number of top routes to process")

    @field_validator('mode')
    @classmethod
    def validate_mode(cls, v: str) -> str:
        """Ensure mode is either 'create' or 'update'."""
        if v not in ['create', 'update']:
            raise ValueError('Mode must be either "create" or "update"')
        return v


class UploadResponse(BaseModel):
    """Schema for parquet upload response with processing summary."""

    file_name: str = Field(..., description="Name of uploaded file")
    rows_read: int = Field(..., ge=0, description="Number of rows read from file")
    zones_created: int = Field(default=0, ge=0, description="Number of zones created")
    zones_updated: int = Field(default=0, ge=0, description="Number of zones updated")
    routes_detected: int = Field(..., ge=0, description="Number of route pairs detected")
    routes_created: int = Field(default=0, ge=0, description="Number of routes created")
    routes_updated: int = Field(default=0, ge=0, description="Number of routes updated")
    errors: List[str] = Field(default_factory=list, description="List of error messages")

    class Config:
        json_schema_extra = {
            "example": {
                "file_name": "yellow_tripdata_2024-01.parquet",
                "rows_read": 50000,
                "zones_created": 0,
                "zones_updated": 0,
                "routes_detected": 120,
                "routes_created": 80,
                "routes_updated": 40,
                "errors": []
            }
        }


# =============================================================================
# Health Check Schema
# =============================================================================
# Simple health check for monitoring API availability.
# GET /health returns {"status": "ok"} if API is running.

class HealthResponse(BaseModel):
    """Schema for health check response."""

    status: str = Field(..., description="API health status")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "ok"
            }
        }


# =============================================================================
# Error Response Schemas
# =============================================================================
# Standard error responses for API failures.
# ErrorDetail: Pydantic validation errors (422) with field location
# ErrorResponse: General errors (400, 404) with simple message

class ErrorDetail(BaseModel):
    """Schema for detailed error information."""

    loc: List[str] = Field(..., description="Location of the error")
    msg: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type")


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    detail: str | List[ErrorDetail] = Field(..., description="Error details")

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Error message describing what went wrong"
            }
        }
