"""
Tests for API endpoints.

Tests the FastAPI endpoints for zones, routes, and uploads.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas import ZoneBase, RouteBase


@pytest.fixture
def client():
    """Create test client for FastAPI app."""
    from app.storage import get_global_storage
    # Clear storage before each test
    storage = get_global_storage()
    storage.clear_all()
    return TestClient(app)


class TestHealthEndpoint:
    """Test suite for health check endpoint."""

    def test_health_check(self, client):
        """Test health check endpoint returns ok status."""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestZonesEndpoints:
    """Test suite for zones CRUD endpoints."""

    def test_create_zone_success(self, client):
        """Test creating a zone successfully."""
        zone_data = {
            "id": 1,
            "borough": "Manhattan",
            "zone_name": "Central Park",
            "service_zone": "Yellow",
            "active": True
        }

        response = client.post("/zones", json=zone_data)

        assert response.status_code == 201
        response_data = response.json()
        assert response_data["id"] == 1
        assert response_data["borough"] == "Manhattan"
        assert response_data["zone_name"] == "Central Park"
        assert response_data["service_zone"] == "Yellow"
        assert response_data["active"] is True
        assert "created_at" in response_data

    def test_create_zone_duplicate_id(self, client):
        """Test creating zone with duplicate ID returns 400."""
        zone_data = {
            "id": 1,
            "borough": "Manhattan",
            "zone_name": "Central Park",
            "service_zone": "Yellow",
            "active": True
        }

        # Create first zone
        client.post("/zones", json=zone_data)

        # Try to create duplicate
        response = client.post("/zones", json=zone_data)

        assert response.status_code == 400
        assert "Value already exists" in response.json()["detail"]

    def test_create_zone_invalid_data(self, client):
        """Test creating zone with invalid data returns 422."""
        zone_data = {
            "id": -1,  # Invalid: must be positive
            "borough": "",  # Invalid: cannot be empty
            "zone_name": "Central Park",
            "service_zone": "Yellow",
            "active": True
        }

        response = client.post("/zones", json=zone_data)

        assert response.status_code == 422

    def test_list_zones_empty(self, client):
        """Test listing zones when empty."""
        response = client.get("/zones")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_zones_with_data(self, client):
        """Test listing zones with data."""
        zone_data = {
            "id": 1,
            "borough": "Manhattan",
            "zone_name": "Central Park",
            "service_zone": "Yellow",
            "active": True
        }
        client.post("/zones", json=zone_data)

        response = client.get("/zones")

        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["id"] == 1

    def test_list_zones_filter_active(self, client):
        """Test filtering zones by active status."""
        # Create active zone
        zone1 = {
            "id": 1,
            "borough": "Manhattan",
            "zone_name": "Central Park",
            "service_zone": "Yellow",
            "active": True
        }
        # Create inactive zone
        zone2 = {
            "id": 2,
            "borough": "Brooklyn",
            "zone_name": "Brooklyn Bridge",
            "service_zone": "Yellow",
            "active": False
        }

        client.post("/zones", json=zone1)
        client.post("/zones", json=zone2)

        response = client.get("/zones?active=true")

        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["id"] == 1

    def test_list_zones_filter_borough(self, client):
        """Test filtering zones by borough."""
        zone1 = {
            "id": 1,
            "borough": "Manhattan",
            "zone_name": "Central Park",
            "service_zone": "Yellow",
            "active": True
        }
        zone2 = {
            "id": 2,
            "borough": "Brooklyn",
            "zone_name": "Brooklyn Bridge",
            "service_zone": "Yellow",
            "active": True
        }

        client.post("/zones", json=zone1)
        client.post("/zones", json=zone2)

        response = client.get("/zones?borough=Manhattan")

        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["borough"] == "Manhattan"

    def test_get_zone_exists(self, client):
        """Test getting an existing zone."""
        zone_data = {
            "id": 1,
            "borough": "Manhattan",
            "zone_name": "Central Park",
            "service_zone": "Yellow",
            "active": True
        }
        client.post("/zones", json=zone_data)

        response = client.get("/zones/1")

        assert response.status_code == 200
        assert response.json()["id"] == 1

    def test_get_zone_not_exists(self, client):
        """Test getting a non-existing zone returns 404."""
        response = client.get("/zones/999")

        assert response.status_code == 404
        assert "zone not found" in response.json()["detail"]

    def test_update_zone_success(self, client):
        """Test updating a zone successfully."""
        # Create zone
        zone_data = {
            "id": 1,
            "borough": "Manhattan",
            "zone_name": "Central Park",
            "service_zone": "Yellow",
            "active": True
        }
        client.post("/zones", json=zone_data)

        # Update zone
        updated_data = {
            "id": 1,
            "borough": "Manhattan",
            "zone_name": "Updated Park",
            "service_zone": "Yellow",
            "active": False
        }

        response = client.put("/zones/1", json=updated_data)

        assert response.status_code == 200
        assert response.json()["zone_name"] == "Updated Park"
        assert response.json()["active"] is False

    def test_update_zone_not_exists(self, client):
        """Test updating a non-existing zone returns 404."""
        updated_data = {
            "id": 999,
            "borough": "Manhattan",
            "zone_name": "Updated Park",
            "service_zone": "Yellow",
            "active": False
        }

        response = client.put("/zones/999", json=updated_data)

        assert response.status_code == 404
        assert "zone not found" in response.json()["detail"]

    def test_update_zone_id_mismatch(self, client):
        """Test updating zone with mismatched ID returns 400."""
        # Create zone
        zone_data = {
            "id": 1,
            "borough": "Manhattan",
            "zone_name": "Central Park",
            "service_zone": "Yellow",
            "active": True
        }
        client.post("/zones", json=zone_data)

        # Try to update with different ID in body
        updated_data = {
            "id": 2,  # Different ID
            "borough": "Manhattan",
            "zone_name": "Updated Park",
            "service_zone": "Yellow",
            "active": False
        }

        response = client.put("/zones/1", json=updated_data)

        assert response.status_code == 400
        assert "Zone ID mismatch" in response.json()["detail"]

    def test_delete_zone_success(self, client):
        """Test deleting a zone successfully."""
        # Create zone
        zone_data = {
            "id": 1,
            "borough": "Manhattan",
            "zone_name": "Central Park",
            "service_zone": "Yellow",
            "active": True
        }
        client.post("/zones", json=zone_data)

        response = client.delete("/zones/1")

        assert response.status_code == 204

        # Verify zone is gone
        response = client.get("/zones/1")
        assert response.status_code == 404

    def test_delete_zone_not_exists(self, client):
        """Test deleting a non-existing zone returns 404."""
        response = client.delete("/zones/999")

        assert response.status_code == 404
        assert "zone not found" in response.json()["detail"]


class TestRoutesEndpoints:
    """Test suite for routes CRUD endpoints."""

    def test_create_route_success(self, client):
        """Test creating a route successfully."""
        # First create zones
        zone1 = {"id": 1, "borough": "A", "zone_name": "Z1", "service_zone": "S", "active": True}
        zone2 = {"id": 2, "borough": "B", "zone_name": "Z2", "service_zone": "S", "active": True}
        client.post("/zones", json=zone1)
        client.post("/zones", json=zone2)

        route_data = {
            "pickup_zone_id": 1,
            "dropoff_zone_id": 2,
            "name": "Route 1 to 2",
            "active": True
        }

        response = client.post("/routes", json=route_data)

        assert response.status_code == 201
        response_data = response.json()
        assert response_data["pickup_zone_id"] == 1
        assert response_data["dropoff_zone_id"] == 2
        assert response_data["name"] == "Route 1 to 2"
        assert response_data["active"] is True
        assert response_data["id"] == 1  # Should be assigned ID 1

    def test_create_route_same_zone(self, client):
        """Test creating route with same pickup/dropoff returns 422 (Pydantic validation)."""
        # Create zone
        zone = {"id": 1, "borough": "A", "zone_name": "Z1", "service_zone": "S", "active": True}
        client.post("/zones", json=zone)

        route_data = {
            "pickup_zone_id": 1,
            "dropoff_zone_id": 1,
            "name": "Invalid Route",
            "active": True
        }

        response = client.post("/routes", json=route_data)

        assert response.status_code == 422  # Pydantic validation error

    def test_create_route_missing_zone(self, client):
        """Test creating route with non-existing zone returns 400."""
        # Create only one zone
        zone = {"id": 1, "borough": "A", "zone_name": "Z1", "service_zone": "S", "active": True}
        client.post("/zones", json=zone)

        route_data = {
            "pickup_zone_id": 1,
            "dropoff_zone_id": 999,  # Doesn't exist
            "name": "Invalid Route",
            "active": True
        }

        response = client.post("/routes", json=route_data)

        assert response.status_code == 400
        assert "dropoff_zone_id not in zones" in response.json()["detail"]

    def test_list_routes_empty(self, client):
        """Test listing routes when empty."""
        response = client.get("/routes")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_routes_with_data(self, client):
        """Test listing routes with data."""
        # Create zones
        zone1 = {"id": 1, "borough": "A", "zone_name": "Z1", "service_zone": "S", "active": True}
        zone2 = {"id": 2, "borough": "B", "zone_name": "Z2", "service_zone": "S", "active": True}
        client.post("/zones", json=zone1)
        client.post("/zones", json=zone2)

        # Create route
        route_data = {
            "pickup_zone_id": 1,
            "dropoff_zone_id": 2,
            "name": "Route 1 to 2",
            "active": True
        }
        client.post("/routes", json=route_data)

        response = client.get("/routes")

        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["pickup_zone_id"] == 1

    def test_get_route_exists(self, client):
        """Test getting an existing route."""
        # Create zones and route
        zone1 = {"id": 1, "borough": "A", "zone_name": "Z1", "service_zone": "S", "active": True}
        zone2 = {"id": 2, "borough": "B", "zone_name": "Z2", "service_zone": "S", "active": True}
        client.post("/zones", json=zone1)
        client.post("/zones", json=zone2)

        route_data = {
            "pickup_zone_id": 1,
            "dropoff_zone_id": 2,
            "name": "Route 1 to 2",
            "active": True
        }
        client.post("/routes", json=route_data)

        response = client.get("/routes/1")

        assert response.status_code == 200
        assert response.json()["id"] == 1

    def test_get_route_not_exists(self, client):
        """Test getting a non-existing route returns 404."""
        response = client.get("/routes/999")

        assert response.status_code == 404
        assert "route not found" in response.json()["detail"]

    def test_update_route_success(self, client):
        """Test updating a route successfully."""
        # Create zones and route
        zone1 = {"id": 1, "borough": "A", "zone_name": "Z1", "service_zone": "S", "active": True}
        zone2 = {"id": 2, "borough": "B", "zone_name": "Z2", "service_zone": "S", "active": True}
        client.post("/zones", json=zone1)
        client.post("/zones", json=zone2)

        route_data = {
            "pickup_zone_id": 1,
            "dropoff_zone_id": 2,
            "name": "Original Route",
            "active": True
        }
        client.post("/routes", json=route_data)

        # Update route
        updated_data = {
            "id": 1,
            "pickup_zone_id": 1,
            "dropoff_zone_id": 2,
            "name": "Updated Route",
            "active": False
        }

        response = client.put("/routes/1", json=updated_data)

        assert response.status_code == 200
        assert response.json()["name"] == "Updated Route"
        assert response.json()["active"] is False

    def test_delete_route_success(self, client):
        """Test deleting a route successfully."""
        # Create zones and route
        zone1 = {"id": 1, "borough": "A", "zone_name": "Z1", "service_zone": "S", "active": True}
        zone2 = {"id": 2, "borough": "B", "zone_name": "Z2", "service_zone": "S", "active": True}
        client.post("/zones", json=zone1)
        client.post("/zones", json=zone2)

        route_data = {
            "pickup_zone_id": 1,
            "dropoff_zone_id": 2,
            "name": "Route to delete",
            "active": True
        }
        client.post("/routes", json=route_data)

        response = client.delete("/routes/1")

        assert response.status_code == 204

        # Verify route is gone
        response = client.get("/routes/1")
        assert response.status_code == 404

    def test_delete_route_not_exists(self, client):
        """Test deleting a non-existing route returns 404."""
        response = client.delete("/routes/999")

        assert response.status_code == 404
        assert "route not found" in response.json()["detail"]


class TestUploadsEndpoints:
    """Test suite for upload endpoints."""

    def test_upload_parquet_invalid_file_type(self, client):
        """Test uploading non-parquet file returns 400."""
        files = {"file": ("test.txt", b"not a parquet file", "text/plain")}
        data = {"mode": "create", "limit_rows": "1000", "top_n_routes": "10"}

        response = client.post("/uploads/trips-parquet", files=files, data=data)

        assert response.status_code == 400
        assert "File must be a .parquet file" in response.json()["detail"]

    def test_upload_parquet_invalid_mode(self, client):
        """Test uploading with invalid mode returns 400."""
        files = {"file": ("test.parquet", b"fake parquet content", "application/octet-stream")}
        data = {"mode": "invalid", "limit_rows": "1000", "top_n_routes": "10"}

        response = client.post("/uploads/trips-parquet", files=files, data=data)

        assert response.status_code == 400
        assert "Invalid mode" in response.json()["detail"]

    def test_upload_parquet_invalid_limit_rows(self, client):
        """Test uploading with invalid limit_rows returns 400."""
        files = {"file": ("test.parquet", b"fake parquet content", "application/octet-stream")}
        data = {"mode": "create", "limit_rows": "0", "top_n_routes": "10"}  # Invalid: must be > 0

        response = client.post("/uploads/trips-parquet", files=files, data=data)

        assert response.status_code == 400
        assert "limit_rows must be between 1 and 1,000,000" in response.json()["detail"]

    def test_upload_parquet_invalid_top_n_routes(self, client):
        """Test uploading with invalid top_n_routes returns 400."""
        files = {"file": ("test.parquet", b"fake parquet content", "application/octet-stream")}
        data = {"mode": "create", "limit_rows": "1000", "top_n_routes": "0"}  # Invalid: must be > 0

        response = client.post("/uploads/trips-parquet", files=files, data=data)

        assert response.status_code == 400
        assert "top_n_routes must be between 1 and 500" in response.json()["detail"]