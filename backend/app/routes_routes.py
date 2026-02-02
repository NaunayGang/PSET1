"""
Routes CRUD endpoints.

This module will implement all CRUD operations for Route resources:
- POST /routes - Create a new route
- GET /routes - List all routes (with optional filters)
- GET /routes/{id} - Get a specific route
- PUT /routes/{id} - Update a route
- DELETE /routes/{id} - Delete a route

TODO: Implement in issue #11
"""

from app.storage import get_global_storage
import logging

from fastapi import APIRouter, HTTPException, status

from app.schemas import RouteBase, RouteCreate

router = APIRouter()

logger = logging.getLogger(__name__)

storage = get_global_storage()


@router.post(
    "/routes",
    response_model=RouteBase,
    status_code=status.HTTP_201_CREATED,
    tags=["Routes"],
)
async def create_route(route: RouteCreate):
    """
    Create a new route.
    """
    logger.debug(
        f"create_route called with pickup={route.pickup_zone_id} dropoff={route.dropoff_zone_id}"
    )

    try:
        # Create RouteBase object with assigned ID
        route_id = storage.assign_route_id()
        route_base = RouteBase(
            id=route_id,
            pickup_zone_id=route.pickup_zone_id,
            dropoff_zone_id=route.dropoff_zone_id,
            name=route.name,
            active=route.active
        )
        logger.debug(f"Assigned route id={route_id}")

        storage.create_route(route_base)
        logger.info(
            f"Route created: id={route_id} pickup={route.pickup_zone_id} dropoff={route.dropoff_zone_id} name={route.name}"
        )

        return route_base
    except ValueError as ve:
        logger.warning(f"create_route failed validation: {ve}")

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as exc:  # unexpected
        logger.exception(f"create_route unexpected error: {exc}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="internal server error",
        )


@router.get("/routes", response_model=list[RouteBase], tags=["Routes"])
async def list_routes(
    active: bool | None = None,
    pickup_zone_id: int | None = None,
    dropoff_zone_id: int | None = None,
):
    """
    List routes with optional filters.
    """
    logger.debug(
        f"list_routes called with filters active={active} pickup={pickup_zone_id} dropoff={dropoff_zone_id}"
    )

    result = storage.get_all_routes(active, pickup_zone_id, dropoff_zone_id)
    logger.info(f"list_routes returning {len(result)} routes")

    return result


@router.get("/routes/{route_id}", response_model=RouteBase, tags=["Routes"])
async def get_route(route_id: int):
    """
    Get a specific route by ID.
    """
    logger.debug(f"get_route called for id={route_id}")

    try:
        result = storage.get_route(route_id)
        if result:
            logger.info(f"Route retrieved: id={result.id} name={result.name}")

            return result
        else:
            logger.info(f"Route not found: id={route_id}")

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="route not found"
            )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as exc:
        logger.exception(f"get_route unexpected error: {exc}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="internal server error",
        )


@router.put("/routes/{route_id}", response_model=RouteBase, tags=["Routes"])
async def update_route(route_id: int, route: RouteBase):
    """
    Update an existing route.
    """
    logger.debug(f"update_route called for id={route_id} payload_id={route.id}")

    try:
        storage.update_route(route_id, route)
        logger.info(f"Route updated: id={route_id} name={route.name}")

        return route
    except ValueError as ve:
        logger.warning(f"update_route failed validation: {ve}")

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as exc:
        logger.exception(f"update_route unexpected error: {exc}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="internal server error",
        )


@router.delete(
    "/routes/{route_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Routes"]
)
async def delete_route(route_id: int):
    """
    Delete a route by ID.
    """
    logger.debug(f"delete_route called for id={route_id}")

    try:
        deleted = storage.delete_route(route_id)
        if deleted:
            logger.info(f"Route deleted: id={route_id}")

            return
        else:
            logger.warning(f"Attempted to delete non-existent route: id={route_id}")

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="route not found"
            )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as exc:
        logger.exception(f"delete_route unexpected error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="internal server error",
        )
