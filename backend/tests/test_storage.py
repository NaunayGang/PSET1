"""
Tests for storage.py module.

Tests the in-memory storage functionality for zones and routes.
"""

import pytest
from app.storage import Storage
from app.schemas import ZoneBase, RouteBase


class TestStorage:
    """Test suite for Storage class."""

    def setup_method(self):
        """Set up fresh storage instance for each test."""
        self.storage = Storage()

    def test_initial_state(self):
        """Test storage starts empty."""
        assert len(self.storage._zones_db) == 0
        assert len(self.storage._routes_db) == 0
        assert self.storage._id_counter == 0

    def test_create_zone_success(self):
        """Test creating a zone successfully."""
        zone = ZoneBase(
            id=1,
            borough="Manhattan",
            zone_name="Central Park",
            service_zone="Yellow",
            active=True
        )

        self.storage.create_zone(zone)

        assert 1 in self.storage._zones_db
        assert self.storage._zones_db[1] == zone

    def test_create_zone_duplicate_id(self):
        """Test creating zone with duplicate ID raises ValueError."""
        zone1 = ZoneBase(id=1, borough="A", zone_name="Z1", service_zone="S", active=True)
        zone2 = ZoneBase(id=1, borough="B", zone_name="Z2", service_zone="S", active=True)

        self.storage.create_zone(zone1)

        with pytest.raises(ValueError, match="Value already exists"):
            self.storage.create_zone(zone2)

    def test_get_zone_exists(self):
        """Test getting an existing zone."""
        zone = ZoneBase(id=1, borough="A", zone_name="Z", service_zone="S", active=True)
        self.storage.create_zone(zone)

        result = self.storage.get_zone(1)
        assert result == zone

    def test_get_zone_not_exists(self):
        """Test getting a non-existing zone returns None."""
        result = self.storage.get_zone(999)
        assert result is None

    def test_get_all_zones_empty(self):
        """Test getting all zones when empty."""
        result = self.storage.get_all_zones()
        assert result == []

    def test_get_all_zones_with_data(self):
        """Test getting all zones with data."""
        zone1 = ZoneBase(id=1, borough="A", zone_name="Z1", service_zone="S", active=True)
        zone2 = ZoneBase(id=2, borough="B", zone_name="Z2", service_zone="S", active=False)
        self.storage.create_zone(zone1)
        self.storage.create_zone(zone2)

        result = self.storage.get_all_zones()
        assert len(result) == 2
        assert zone1 in result
        assert zone2 in result

    def test_get_all_zones_filter_active(self):
        """Test filtering zones by active status."""
        zone1 = ZoneBase(id=1, borough="A", zone_name="Z1", service_zone="S", active=True)
        zone2 = ZoneBase(id=2, borough="B", zone_name="Z2", service_zone="S", active=False)
        self.storage.create_zone(zone1)
        self.storage.create_zone(zone2)

        result = self.storage.get_all_zones(active=True)
        assert len(result) == 1
        assert result[0] == zone1

    def test_get_all_zones_filter_borough(self):
        """Test filtering zones by borough."""
        zone1 = ZoneBase(id=1, borough="Manhattan", zone_name="Z1", service_zone="S", active=True)
        zone2 = ZoneBase(id=2, borough="Brooklyn", zone_name="Z2", service_zone="S", active=True)
        self.storage.create_zone(zone1)
        self.storage.create_zone(zone2)

        result = self.storage.get_all_zones(borough="Manhattan")
        assert len(result) == 1
        assert result[0] == zone1

    def test_update_zone_success(self):
        """Test updating a zone successfully."""
        zone = ZoneBase(id=1, borough="A", zone_name="Z", service_zone="S", active=True)
        self.storage.create_zone(zone)

        updated_zone = ZoneBase(id=1, borough="B", zone_name="Updated", service_zone="S", active=False)
        self.storage.update_zone(updated_zone)

        result = self.storage.get_zone(1)
        assert result == updated_zone

    def test_delete_zone_success(self):
        """Test deleting an existing zone."""
        zone = ZoneBase(id=1, borough="A", zone_name="Z", service_zone="S", active=True)
        self.storage.create_zone(zone)

        result = self.storage.delete_zone(1)
        assert result is True
        assert 1 not in self.storage._zones_db

    def test_delete_zone_not_exists(self):
        """Test deleting a non-existing zone."""
        result = self.storage.delete_zone(999)
        assert result is False

    def test_zone_exists(self):
        """Test checking if zone exists."""
        zone = ZoneBase(id=1, borough="A", zone_name="Z", service_zone="S", active=True)
        self.storage.create_zone(zone)

        assert self.storage.zone_exists(1) is True
        assert self.storage.zone_exists(999) is False

    # Route tests
    def test_create_route_success(self):
        """Test creating a route successfully."""
        # First create zones
        zone1 = ZoneBase(id=1, borough="A", zone_name="Z1", service_zone="S", active=True)
        zone2 = ZoneBase(id=2, borough="B", zone_name="Z2", service_zone="S", active=True)
        self.storage.create_zone(zone1)
        self.storage.create_zone(zone2)

        route = RouteBase(id=1, pickup_zone_id=1, dropoff_zone_id=2, name="Route 1-2", active=True)
        self.storage.create_route(route)

        assert 1 in self.storage._routes_db
        assert self.storage._routes_db[1] == route

    def test_create_route_same_pickup_dropoff(self):
        """Test creating route with same pickup and dropoff raises ValueError."""
        # Note: This validation now happens at the schema level, not storage level
        zone1 = ZoneBase(id=1, borough="A", zone_name="Z1", service_zone="S", active=True)
        self.storage.create_zone(zone1)

        # This should fail at schema validation
        with pytest.raises(Exception):  # Could be ValidationError from Pydantic
            route = RouteBase(id=1, pickup_zone_id=1, dropoff_zone_id=1, name="Invalid", active=True)

    def test_create_route_missing_zone(self):
        """Test creating route with non-existing zone raises ValueError."""
        zone1 = ZoneBase(id=1, borough="A", zone_name="Z1", service_zone="S", active=True)
        self.storage.create_zone(zone1)

        route = RouteBase(id=1, pickup_zone_id=1, dropoff_zone_id=999, name="Invalid", active=True)

        with pytest.raises(ValueError, match="dropoff_zone_id not in zones"):
            self.storage.create_route(route)

    def test_get_route_exists(self):
        """Test getting an existing route."""
        # Setup zones and route
        zone1 = ZoneBase(id=1, borough="A", zone_name="Z1", service_zone="S", active=True)
        zone2 = ZoneBase(id=2, borough="B", zone_name="Z2", service_zone="S", active=True)
        self.storage.create_zone(zone1)
        self.storage.create_zone(zone2)

        route = RouteBase(id=1, pickup_zone_id=1, dropoff_zone_id=2, name="Route 1-2", active=True)
        self.storage.create_route(route)

        result = self.storage.get_route(1)
        assert result == route

    def test_get_all_routes_with_filters(self):
        """Test getting all routes with filters."""
        # Setup zones
        zone1 = ZoneBase(id=1, borough="A", zone_name="Z1", service_zone="S", active=True)
        zone2 = ZoneBase(id=2, borough="B", zone_name="Z2", service_zone="S", active=True)
        zone3 = ZoneBase(id=3, borough="C", zone_name="Z3", service_zone="S", active=True)
        self.storage.create_zone(zone1)
        self.storage.create_zone(zone2)
        self.storage.create_zone(zone3)

        # Setup routes
        route1 = RouteBase(id=1, pickup_zone_id=1, dropoff_zone_id=2, name="R1", active=True)
        route2 = RouteBase(id=2, pickup_zone_id=1, dropoff_zone_id=3, name="R2", active=False)
        route3 = RouteBase(id=3, pickup_zone_id=2, dropoff_zone_id=3, name="R3", active=True)
        self.storage.create_route(route1)
        self.storage.create_route(route2)
        self.storage.create_route(route3)

        # Test active filter
        result = self.storage.get_all_routes(active=True)
        assert len(result) == 2
        assert route1 in result
        assert route3 in result

        # Test pickup_zone_id filter
        result = self.storage.get_all_routes(pickup_zone_id=1)
        assert len(result) == 2
        assert route1 in result
        assert route2 in result

        # Test dropoff_zone_id filter
        result = self.storage.get_all_routes(dropoff_zone_id=3)
        assert len(result) == 2
        assert route2 in result
        assert route3 in result

    def test_find_route_by_zones(self):
        """Test finding route by pickup and dropoff zones."""
        # Setup zones and route
        zone1 = ZoneBase(id=1, borough="A", zone_name="Z1", service_zone="S", active=True)
        zone2 = ZoneBase(id=2, borough="B", zone_name="Z2", service_zone="S", active=True)
        self.storage.create_zone(zone1)
        self.storage.create_zone(zone2)

        route = RouteBase(id=1, pickup_zone_id=1, dropoff_zone_id=2, name="Route 1-2", active=True)
        self.storage.create_route(route)

        result = self.storage.find_route_by_zones(1, 2)
        assert result == route

        result = self.storage.find_route_by_zones(2, 1)
        assert result is None

    def test_update_route_success(self):
        """Test updating a route successfully."""
        # Setup zones and route
        zone1 = ZoneBase(id=1, borough="A", zone_name="Z1", service_zone="S", active=True)
        zone2 = ZoneBase(id=2, borough="B", zone_name="Z2", service_zone="S", active=True)
        self.storage.create_zone(zone1)
        self.storage.create_zone(zone2)

        route = RouteBase(id=1, pickup_zone_id=1, dropoff_zone_id=2, name="Original", active=True)
        self.storage.create_route(route)

        updated_route = RouteBase(id=1, pickup_zone_id=1, dropoff_zone_id=2, name="Updated", active=False)
        self.storage.update_route(1, updated_route)

        result = self.storage.get_route(1)
        assert result == updated_route

    def test_delete_route_success(self):
        """Test deleting a route successfully."""
        # Setup zones and route
        zone1 = ZoneBase(id=1, borough="A", zone_name="Z1", service_zone="S", active=True)
        zone2 = ZoneBase(id=2, borough="B", zone_name="Z2", service_zone="S", active=True)
        self.storage.create_zone(zone1)
        self.storage.create_zone(zone2)

        route = RouteBase(id=1, pickup_zone_id=1, dropoff_zone_id=2, name="Route", active=True)
        self.storage.create_route(route)

        result = self.storage.delete_route(1)
        assert result is True
        assert 1 not in self.storage._routes_db

    def test_clear_all(self):
        """Test clearing all data."""
        # Setup some data
        zone = ZoneBase(id=1, borough="A", zone_name="Z", service_zone="S", active=True)
        self.storage.create_zone(zone)

        self.storage.clear_all()

        assert len(self.storage._zones_db) == 0
        assert len(self.storage._routes_db) == 0

    def test_get_storage_stats(self):
        """Test getting storage statistics."""
        # Setup some data
        zone1 = ZoneBase(id=1, borough="A", zone_name="Z1", service_zone="S", active=True)
        zone2 = ZoneBase(id=2, borough="B", zone_name="Z2", service_zone="S", active=True)
        self.storage.create_zone(zone1)
        self.storage.create_zone(zone2)

        zone3 = ZoneBase(id=3, borough="C", zone_name="Z3", service_zone="S", active=True)
        self.storage.create_zone(zone3)

        # Setup routes
        route1 = RouteBase(id=1, pickup_zone_id=1, dropoff_zone_id=2, name="R1", active=True)
        route2 = RouteBase(id=2, pickup_zone_id=2, dropoff_zone_id=3, name="R2", active=True)
        self.storage.create_route(route1)
        self.storage.create_route(route2)

        stats = self.storage.get_storage_stats()
        assert stats["zones_count"] == 3
        assert stats["routes_count"] == 2

    def test_assign_route_id(self):
        """Test assigning route IDs."""
        id1 = self.storage.assign_route_id()
        id2 = self.storage.assign_route_id()

        assert id1 == 1
        assert id2 == 2
        assert self.storage._id_counter == 2