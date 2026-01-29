"""
Zones CRUD endpoints.

This module implements all CRUD operations for Zone resources:
- POST /zones - Create a new zone
- GET /zones - List all zones (with optional filters)
- GET /zones/{id} - Get a specific zone
- PUT /zones/{id} - Update a zone
- DELETE /zones/{id} - Delete a zone

Issue #10: Implement Zones Endpoints
"""

from app.storage import get_global_storage
import logging

from fastapi import APIRouter, HTTPException, status

from app.schemas import ZoneBase

router = APIRouter()

logger = logging.getLogger(__name__)

storage = get_global_storage()


@router.post(
    "/zones",
    response_model=ZoneBase,
    status_code=status.HTTP_201_CREATED,
    tags=["Zones"],
)
async def create_zone(zone: ZoneBase):
    """
    Create a new zone.

    Args:
        zone: Zone data with id, borough, zone_name, service_zone, active

    Returns:
        Created zone

    Raises:
        400: Zone with this ID already exists or validation errors
        422: Invalid request body
    """
    logger.debug(
        f"create_zone called with id={zone.id} borough={zone.borough} name={zone.zone_name}"
    )

    try:
        storage.create_zone(zone)
        logger.info(
            f"Zone created: id={zone.id} borough={zone.borough} zone_name={zone.zone_name}"
        )

        return zone
    except ValueError as ve:
        logger.warning(f"create_zone failed validation: {ve}")

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as exc:  # unexpected
        logger.exception(f"create_zone unexpected error: {exc}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="internal server error",
        )


@router.get("/zones", response_model=list[ZoneBase], tags=["Zones"])
async def list_zones(
    active: bool | None = None,
    borough: str | None = None,
):
    """
    List zones with optional filters.

    Args:
        active: Filter by active status (True/False)
        borough: Filter by borough name

    Returns:
        List of zones matching filters
    """
    logger.debug(
        f"list_zones called with filters active={active} borough={borough}"
    )

    result = storage.get_all_zones(active, borough)
    logger.info(f"list_zones returning {len(result)} zones")

    return result


@router.get("/zones/{zone_id}", response_model=ZoneBase, tags=["Zones"])
async def get_zone(zone_id: int):
    """
    Get a specific zone by ID.

    Args:
        zone_id: Zone ID to retrieve

    Returns:
        Zone with specified ID

    Raises:
        404: Zone not found
    """
    logger.debug(f"get_zone called for id={zone_id}")

    try:
        result = storage.get_zone(zone_id)
        if result:
            logger.info(f"Zone retrieved: id={result.id} name={result.zone_name}")

            return result
        else:
            logger.info(f"Zone not found: id={zone_id}")

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="zone not found"
            )
    except Exception as exc:
        logger.exception(f"get_zone unexpected error: {exc}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="internal server error",
        )


@router.put("/zones/{zone_id}", response_model=ZoneBase, tags=["Zones"])
async def update_zone(zone_id: int, zone: ZoneBase):
    """
    Update an existing zone.

    Args:
        zone_id: Zone ID to update (must match zone.id in body)
        zone: Updated zone data

    Returns:
        Updated zone

    Raises:
        400: Validation errors (empty fields, invalid ID)
        404: Zone not found
    """
    logger.debug(f"update_zone called for id={zone_id} payload_id={zone.id}")

    try:
        # Verify zone exists before updating
        if not storage.zone_exists(zone_id):
            logger.warning(f"Attempted to update non-existent zone: id={zone_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="zone not found"
            )

        # Verify zone_id matches payload
        if zone_id != zone.id:
            logger.warning(
                f"Zone ID mismatch: URL id={zone_id}, payload id={zone.id}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Zone ID mismatch: URL id={zone_id}, payload id={zone.id}"
            )

        storage.update_zone(zone)
        logger.info(f"Zone updated: id={zone_id} name={zone.zone_name}")

        return zone
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValueError as ve:
        logger.warning(f"update_zone failed validation: {ve}")

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as exc:
        logger.exception(f"update_zone unexpected error: {exc}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="internal server error",
        )


@router.delete(
    "/zones/{zone_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Zones"]
)
async def delete_zone(zone_id: int):
    """
    Delete a zone by ID.

    Args:
        zone_id: Zone ID to delete

    Returns:
        204 No Content on success

    Raises:
        404: Zone not found
    """
    logger.debug(f"delete_zone called for id={zone_id}")

    try:
        deleted = storage.delete_zone(zone_id)
        if deleted:
            logger.info(f"Zone deleted: id={zone_id}")

            return
        else:
            logger.warning(f"Attempted to delete non-existent zone: id={zone_id}")

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="zone not found"
            )
    except Exception as exc:
        logger.exception(f"delete_zone unexpected error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="internal server error",
        )
