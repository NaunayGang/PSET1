"""
Storage management for in-memory parquet file handling.

This module provides:
- In-memory storage for Zones and Routes using dicts
- CRUD operations for entities
- Parquet file reading and processing

The storage is in ram, so it doesnt survive reboots.
"""

import logging


from app.schemas import (
    RouteBase,
    ZoneBase,
)

# Configure logging for storage operations
# usefull for debugging
logger = logging.getLogger(__name__)


class Storage:
    """
    In-memory storage for Zones and Routes.

    Attributes:
        _zones_db: Dictionary mapping zone_id -> zone_data
        _routes_db: Dictionary mapping route_id -> route_data
    """

    def __init__(self):
        """
        Initialize storage with empty dictionaries.
        """
        self._zones_db: dict[int, ZoneBase] = {}
        self._routes_db: dict[int, RouteBase] = {}

    # Zone Operations (CRUD)

    def create_zone(self, zone: ZoneBase):
        """
        Create a new zone in storage.

        Args:
            zone: ZoneBase schema containing zone data

        Raises:
            ValueError: If the id is already in the storage
        """
        if zone.id in self._zones_db:
            logger.warning(f"Attempted to create zone with duplicate ID: {zone.id}")
            raise ValueError("Value already exists")
        else:
            self._zones_db[zone.id] = zone
            logger.info(f"Zone created: id={zone.id}, borough={zone.borough}, zone_name={zone.zone_name}")

    def get_zone(self, zone_id: int) -> ZoneBase | None:
        """
        Retrieve a zone by ID.

        Args:
            zone_id: The zone ID to retrieve

        Returns:
            ZoneBase: The zone if found, None otherwise
        """
        zone = self._zones_db.get(zone_id)
        if zone:
            logger.debug(f"Zone retrieved: id={zone_id}")
        else:
            logger.debug(f"Zone not found: id={zone_id}")
        return zone

    def get_all_zones(
        self,
        active: bool | None = None,
        borough: str | None = None,
    ) -> list[ZoneBase]:
        """
        Retrieve all zones with optional filtering.

        Args:
            active: Filter by active status (True/False). None = no filter
            borough: Filter by borough name. None = no filter

        Returns:
            List[ZoneResponse]: List of matching zones, ordered by creation time
        """
        ret = list(self._zones_db.values())
        if active is not None:
            ret = [i for i in ret if i.active == active]
        if borough:
            ret = [i for i in ret if i.borough == borough]

        logger.debug(f"Retrieved {len(ret)} zones with filters: active={active}, borough={borough}")
        return ret

    def update_zone(self, zone: ZoneBase):
        """
        Update a zone by ID.

        Args:
            zone: ZoneBase schema with new zone data. The zone.id determines which zone to update.
        """
        self._zones_db[zone.id] = zone
        logger.info(f"Zone updated: id={zone.id}, borough={zone.borough}, zone_name={zone.zone_name}")

    def delete_zone(self, zone_id: int) -> bool:
        """
        Delete a zone from storage.

        Args:
            zone_id: The ID of the zone to delete

        Returns:
            bool: True if deleted successfully, False if zone_id not found
        """
        if zone_id in self._zones_db:
            del self._zones_db[zone_id]
            logger.info(f"Zone deleted: id={zone_id}")
            return True

        logger.warning(f"Attempted to delete non-existent zone: id={zone_id}")
        return False

    def zone_exists(self, zone_id: int) -> bool:
        """
        Check if a zone exists in storage.

        Args:
            zone_id: The zone ID to check

        Returns:
            bool: True if zone exists, False otherwise
        """
        return zone_id in self._zones_db

    # Route Operations (CRUD)

    def create_route(self, route: RouteBase):
        """
        Create a new route in storage.

        Args:
            route: RouteBase schema containing route data

        Raises:
            ValueError: If pickup_zone_id == dropoff_zone_id, zones don't exist, or value already exists
        """

        if route.id in self._routes_db:
            logger.warning(f"Attempted to create route with duplicate ID: {route.id}")
            raise ValueError("Value already exists")
        elif route.pickup_zone_id == route.dropoff_zone_id:
            logger.warning(f"Attempted to create route with same pickup/dropoff: {route.pickup_zone_id}")
            raise ValueError("pickup_zone_id == dropoff_zone_id")
        elif route.dropoff_zone_id not in self._zones_db:
            logger.warning(f"Attempted to create route with non-existent dropoff zone: {route.dropoff_zone_id}")
            raise ValueError("dropoff_zone_id not in zones")
        elif route.pickup_zone_id not in self._zones_db:
            logger.warning(f"Attempted to create route with non-existent pickup zone: {route.pickup_zone_id}")
            raise ValueError("pickup_zone_id not in zones")
        else:
            self._routes_db[route.id] = route
            logger.info(f"Route created: id={route.id}, pickup={route.pickup_zone_id}, dropoff={route.dropoff_zone_id}, name={route.name}")

    def get_route(self, route_id: int) -> RouteBase | None:
        """
        Retrieve a route by ID.

        Args:
            route_id: The route ID to retrieve

        Returns:
            RouteBase: The route if found, None otherwise
        """
        route = self._routes_db.get(route_id)
        if route:
            logger.debug(f"Route retrieved: id={route_id}")
        else:
            logger.debug(f"Route not found: id={route_id}")
        return route

    def get_all_routes(
        self,
        active: bool = False,
        pickup_zone_id: int | None = None,
        dropoff_zone_id: int | None = None,
    ) -> list[RouteBase]:
        """
        Retrieve all routes with optional filtering.

        Args:
            active: Filter by active status (True/False). None = no filter
            pickup_zone_id: Filter by pickup zone ID. None = no filter
            dropoff_zone_id: Filter by dropoff zone ID. None = no filter

        Returns:
            List[RouteResponse]: List of matching routes, ordered by creation time
        """
        ret = list(self._routes_db.values())
        if active:
            ret = [i for i in ret if i.active]
        if pickup_zone_id:
            ret = [i for i in ret if i.pickup_zone_id == pickup_zone_id]
        if dropoff_zone_id:
            ret = [i for i in ret if i.dropoff_zone_id == dropoff_zone_id]

        logger.debug(f"Retrieved {len(ret)} routes with filters: active={active}, pickup={pickup_zone_id}, dropoff={dropoff_zone_id}")
        return ret

    def find_route_by_zones(
        self,
        pickup_zone_id: int,
        dropoff_zone_id: int,
    ) -> RouteBase | None:
        """
        Find a route by pickup and dropoff zone IDs (upsert lookup).

        Args:
            pickup_zone_id: The pickup zone ID
            dropoff_zone_id: The dropoff zone ID

        Returns:
            RouteResponse: The route if found, None otherwise
        """
        for value in self._routes_db.values():
            if (
                value.pickup_zone_id == pickup_zone_id
                and value.dropoff_zone_id == dropoff_zone_id
            ):
                logger.debug(f"Route found for zone pair: pickup={pickup_zone_id}, dropoff={dropoff_zone_id}, route_id={value.id}")
                return value

        logger.debug(f"Route not found for zone pair: pickup={pickup_zone_id}, dropoff={dropoff_zone_id}")
        return None

    def update_route(self, route_id: int, route: RouteBase):
        """
        Update an existing route. Same as create_route but doesnt check for existing values, only replaces them.

        Args:
            route_id: The ID of the route to update
            route: RouteBase schema with new route data

        Raises:
            ValueError: If pickup_zone_id == dropoff_zone_id or zones don't exist or route_id != route.id
        """

        if route.pickup_zone_id == route.dropoff_zone_id:
            logger.warning(f"Attempted to update route with same pickup/dropoff: {route.pickup_zone_id}")
            raise ValueError("pickup_zone_id == dropoff_zone_id")
        elif route.dropoff_zone_id not in self._zones_db:
            logger.warning(f"Attempted to update route with non-existent dropoff zone: {route.dropoff_zone_id}")
            raise ValueError("dropoff_zone_id not in zones")
        elif route.pickup_zone_id not in self._zones_db:
            logger.warning(f"Attempted to update route with non-existent pickup zone: {route.pickup_zone_id}")
            raise ValueError("pickup_zone_id not in zones")
        elif route_id != route.id:
            logger.warning(f"Attempted to update route with mismatched IDs: route_id={route_id}, route.id={route.id}")
            raise ValueError("route_id != route.id")
        else:
            self._routes_db[route_id] = route
            logger.info(f"Route updated: id={route_id}, pickup={route.pickup_zone_id}, dropoff={route.dropoff_zone_id}, name={route.name}")

    def delete_route(self, route_id: int) -> bool:
        """
        Delete a route from storage.

        Args:
            route_id: The ID of the route to delete

        Returns:
            bool: True if deleted successfully, False if route_id not found
        """
        if route_id in self._routes_db:
            del self._routes_db[route_id]
            logger.info(f"Route deleted: id={route_id}")
            return True

        logger.warning(f"Attempted to delete non-existent route: id={route_id}")
        return False

    def route_exists(self, route_id: int) -> bool:
        """
        Check if a route exists in storage.

        Args:
            route_id: The route ID to check

        Returns:
            bool: True if route exists, False otherwise
        """
        return route_id in self._routes_db

    # Utility Methods

    def clear_all(self) -> None:
        """
        Clear all data from storage (for testing purposes).

        This method resets both zones and routes to empty state.
        Use with caution in production.
        """
        self._routes_db.clear()
        self._zones_db.clear()
        logger.info("Storage cleared: all zones and routes removed")

    def get_storage_stats(self) -> dict[str, int]:
        """
        Get statistics about current storage state.

        Returns:
            dict: Dictionary with keys 'zones_count', 'routes_count'
        """
        stats = {
            "zones_count": len(self._zones_db.keys()),
            "routes_count": len(self._routes_db.keys()),
        }
        logger.debug(f"Storage stats: {stats}")
        return stats
