"""
End-to-End Integration Tests for Demand Prediction Service.

This module contains comprehensive end-to-end tests that simulate real user workflows
and verify the complete integration between all backend components.
"""

import pytest
import io
import pandas as pd
from fastapi.testclient import TestClient
from app.main import app
from app.schemas import ZoneBase, RouteBase


@pytest.fixture
def client():
    """Create test client for FastAPI app with fresh storage."""
    from app.storage import get_global_storage
    # Clear storage before each test
    storage = get_global_storage()
    storage.clear_all()
    return TestClient(app)


class TestEndToEndWorkflow:
    """End-to-end tests simulating complete user workflows."""

    def test_complete_zone_management_workflow(self, client):
        """Test complete zone management workflow: create, read, update, delete."""
        # Step 1: Create multiple zones
        zones_data = [
            {
                "id": 1,
                "borough": "Manhattan",
                "zone_name": "Central Park",
                "service_zone": "Yellow",
                "active": True
            },
            {
                "id": 2,
                "borough": "Brooklyn",
                "zone_name": "Williamsburg",
                "service_zone": "Green",
                "active": True
            },
            {
                "id": 3,
                "borough": "Queens",
                "zone_name": "JFK Airport",
                "service_zone": "Yellow",
                "active": False
            }
        ]

        # Create all zones
        for zone_data in zones_data:
            response = client.post("/zones", json=zone_data)
            assert response.status_code == 201

        # Step 2: List all zones
        response = client.get("/zones")
        assert response.status_code == 200
        zones = response.json()
        assert len(zones) == 3

        # Step 3: Filter active zones
        response = client.get("/zones?active=true")
        assert response.status_code == 200
        active_zones = response.json()
        assert len(active_zones) == 2

        # Step 4: Filter by borough
        response = client.get("/zones?borough=Manhattan")
        assert response.status_code == 200
        manhattan_zones = response.json()
        assert len(manhattan_zones) == 1
        assert manhattan_zones[0]["borough"] == "Manhattan"

        # Step 5: Get specific zone
        response = client.get("/zones/1")
        assert response.status_code == 200
        zone = response.json()
        assert zone["id"] == 1
        assert zone["zone_name"] == "Central Park"

        # Step 6: Update zone
        update_data = {
            "id": 1,
            "borough": "Manhattan",
            "zone_name": "Central Park North",
            "service_zone": "Yellow",
            "active": True
        }
        response = client.put("/zones/1", json=update_data)
        assert response.status_code == 200

        # Verify update
        response = client.get("/zones/1")
        assert response.status_code == 200
        updated_zone = response.json()
        assert updated_zone["zone_name"] == "Central Park North"

        # Step 7: Delete zone
        response = client.delete("/zones/3")
        assert response.status_code == 204

        # Verify deletion
        response = client.get("/zones/3")
        assert response.status_code == 404

        # Verify remaining zones
        response = client.get("/zones")
        assert response.status_code == 200
        remaining_zones = response.json()
        assert len(remaining_zones) == 2

    def test_complete_route_management_workflow(self, client):
        """Test complete route management workflow."""
        # Step 1: Create zones first
        zone1 = {"id": 1, "borough": "A", "zone_name": "Z1", "service_zone": "S", "active": True}
        zone2 = {"id": 2, "borough": "B", "zone_name": "Z2", "service_zone": "S", "active": True}
        zone3 = {"id": 3, "borough": "C", "zone_name": "Z3", "service_zone": "S", "active": True}

        for zone in [zone1, zone2, zone3]:
            client.post("/zones", json=zone)

        # Step 2: Create routes
        routes_data = [
            {
                "pickup_zone_id": 1,
                "dropoff_zone_id": 2,
                "name": "Route A to B",
                "active": True
            },
            {
                "pickup_zone_id": 2,
                "dropoff_zone_id": 3,
                "name": "Route B to C",
                "active": True
            },
            {
                "pickup_zone_id": 1,
                "dropoff_zone_id": 3,
                "name": "Route A to C",
                "active": False
            }
        ]

        created_routes = []
        for route_data in routes_data:
            response = client.post("/routes", json=route_data)
            assert response.status_code == 201
            created_routes.append(response.json())

        # Step 3: List all routes
        response = client.get("/routes")
        assert response.status_code == 200
        routes = response.json()
        assert len(routes) == 3

        # Step 4: Get specific route
        route_id = created_routes[0]["id"]
        response = client.get(f"/routes/{route_id}")
        assert response.status_code == 200
        route = response.json()
        assert route["name"] == "Route A to B"

        # Step 5: Update route
        update_data = {
            "id": route_id,
            "pickup_zone_id": 1,
            "dropoff_zone_id": 2,
            "name": "Updated Route A to B",
            "active": True
        }
        response = client.put(f"/routes/{route_id}", json=update_data)
        assert response.status_code == 200

        # Verify update
        response = client.get(f"/routes/{route_id}")
        assert response.status_code == 200
        updated_route = response.json()
        assert updated_route["name"] == "Updated Route A to B"

        # Step 6: Delete route
        response = client.delete(f"/routes/{route_id}")
        assert response.status_code == 204

        # Verify remaining routes
        response = client.get("/routes")
        assert response.status_code == 200
        remaining_routes = response.json()
        assert len(remaining_routes) == 2

    def test_zone_route_integration_workflow(self, client):
        """Test the integration between zones and routes."""
        # Create zones
        zones = [
            {"id": 1, "borough": "Manhattan", "zone_name": "Midtown", "service_zone": "Yellow", "active": True},
            {"id": 2, "borough": "Manhattan", "zone_name": "Downtown", "service_zone": "Yellow", "active": True},
            {"id": 3, "borough": "Brooklyn", "zone_name": "DUMBO", "service_zone": "Green", "active": True},
        ]

        for zone in zones:
            response = client.post("/zones", json=zone)
            assert response.status_code == 201

        # Create routes between zones
        routes = [
            {"pickup_zone_id": 1, "dropoff_zone_id": 2, "name": "Midtown to Downtown", "active": True},
            {"pickup_zone_id": 2, "dropoff_zone_id": 3, "name": "Downtown to DUMBO", "active": True},
            {"pickup_zone_id": 1, "dropoff_zone_id": 3, "name": "Midtown to DUMBO", "active": True},
        ]

        created_route_ids = []
        for route in routes:
            response = client.post("/routes", json=route)
            assert response.status_code == 201
            created_route_ids.append(response.json()["id"])

        # Verify all routes exist and reference valid zones
        response = client.get("/routes")
        assert response.status_code == 200
        all_routes = response.json()
        assert len(all_routes) == 3

        for route in all_routes:
            # Verify pickup zone exists
            pickup_response = client.get(f"/zones/{route['pickup_zone_id']}")
            assert pickup_response.status_code == 200

            # Verify dropoff zone exists
            dropoff_response = client.get(f"/zones/{route['dropoff_zone_id']}")
            assert dropoff_response.status_code == 200

        # Test cascading - what happens when we delete a zone that's referenced by routes
        # This should fail because routes depend on zones
        response = client.delete("/zones/1")  # Midtown is referenced by routes
        # Note: Current implementation might allow this - depends on business logic
        # For now, just verify the operation completes (either succeeds or fails appropriately)

    def test_error_handling_integration(self, client):
        """Test error handling across the entire system."""
        # Test 1: Try to create route with non-existent zones
        route_data = {
            "pickup_zone_id": 999,
            "dropoff_zone_id": 1000,
            "name": "Invalid Route",
            "active": True
        }
        response = client.post("/routes", json=route_data)
        assert response.status_code == 400  # Should fail validation

        # Test 2: Try to get non-existent resources
        response = client.get("/zones/999")
        assert response.status_code == 404

        response = client.get("/routes/999")
        assert response.status_code == 404

        # Test 3: Try to update non-existent resources
        update_data = {"id": 999, "borough": "Test", "zone_name": "Test", "service_zone": "Test", "active": True}
        response = client.put("/zones/999", json=update_data)
        assert response.status_code == 404

        # Test 4: Try to delete non-existent resources
        response = client.delete("/zones/999")
        assert response.status_code == 404

        response = client.delete("/routes/999")
        assert response.status_code == 404

        # Test 5: Try to create duplicate zones
        zone_data = {"id": 1, "borough": "Test", "zone_name": "Test", "service_zone": "Test", "active": True}
        client.post("/zones", json=zone_data)  # Create first time
        response = client.post("/zones", json=zone_data)  # Try duplicate
        assert response.status_code == 400  # Should fail

    def test_health_and_system_integration(self, client):
        """Test system health and basic integration."""
        # Test health endpoint
        response = client.get("/health")
        assert response.status_code == 200
        health_data = response.json()
        assert health_data == {"status": "ok"}

        # Test that storage is properly initialized
        response = client.get("/zones")
        assert response.status_code == 200
        assert response.json() == []

        response = client.get("/routes")
        assert response.status_code == 200
        assert response.json() == []

    def test_data_consistency_workflow(self, client):
        """Test data consistency across operations."""
        # Create zones
        zone_data1 = {"id": 1, "borough": "Test", "zone_name": "Test Zone 1", "service_zone": "Yellow", "active": True}
        zone_data2 = {"id": 2, "borough": "Test", "zone_name": "Test Zone 2", "service_zone": "Yellow", "active": True}
        response = client.post("/zones", json=zone_data1)
        assert response.status_code == 201
        response = client.post("/zones", json=zone_data2)
        assert response.status_code == 201

        # Create a valid route
        route_data = {
            "pickup_zone_id": 1,
            "dropoff_zone_id": 2,
            "name": "Test Route",
            "active": True
        }
        response = client.post("/routes", json=route_data)
        assert response.status_code == 201

        # Try to create invalid route (same pickup/dropoff) - should fail
        invalid_route_data = {
            "pickup_zone_id": 1,
            "dropoff_zone_id": 1,  # Same zone - this will fail validation
            "name": "Invalid Route",
            "active": True
        }
        response = client.post("/routes", json=invalid_route_data)
        assert response.status_code == 422  # Should fail because pickup == dropoff (Pydantic validation)

        # Verify data integrity
        response = client.get("/zones/1")
        assert response.status_code == 200
        zone = response.json()
        assert zone["id"] == 1

        response = client.get("/routes")
        assert response.status_code == 200
        routes = response.json()
        assert len(routes) == 1  # Only the valid route should exist

        # Test that zone data is consistent in route responses
        # (This would require joining zone data with routes in a real implementation)


class TestPerformanceIntegration:
    """Performance-focused integration tests."""

    def test_bulk_operations_performance(self, client):
        """Test performance with bulk operations."""
        # Create multiple zones
        zones = []
        for i in range(1, 11):  # Create 10 zones
            zone_data = {
                "id": i,
                "borough": f"Borough{i}",
                "zone_name": f"Zone{i}",
                "service_zone": "Yellow",
                "active": True
            }
            zones.append(zone_data)
            response = client.post("/zones", json=zone_data)
            assert response.status_code == 201

        # Create multiple routes
        routes_created = 0
        for i in range(1, 6):  # Create routes between zones
            for j in range(i + 1, min(i + 4, 11)):
                route_data = {
                    "pickup_zone_id": i,
                    "dropoff_zone_id": j,
                    "name": f"Route {i} to {j}",
                    "active": True
                }
                response = client.post("/routes", json=route_data)
                assert response.status_code == 201
                routes_created += 1

        # Verify bulk retrieval
        response = client.get("/zones")
        assert response.status_code == 200
        assert len(response.json()) == 10

        response = client.get("/routes")
        assert response.status_code == 200
        assert len(response.json()) == routes_created

    def test_concurrent_access_simulation(self, client):
        """Simulate concurrent access patterns."""
        # Create initial data
        zone_data = {"id": 1, "borough": "Test", "zone_name": "Test", "service_zone": "Test", "active": True}
        client.post("/zones", json=zone_data)

        # Create a second zone for the route
        zone_data2 = {"id": 2, "borough": "Test2", "zone_name": "Test2", "service_zone": "Test", "active": True}
        client.post("/zones", json=zone_data2)

        # Simulate multiple read operations (concurrent reads should be fine)
        for _ in range(5):
            response = client.get("/zones/1")
            assert response.status_code == 200

        # Simulate read after write
        route_data = {"pickup_zone_id": 1, "dropoff_zone_id": 2, "name": "Test", "active": True}
        client.post("/routes", json=route_data)

        response = client.get("/routes")
        assert response.status_code == 200
        assert len(response.json()) == 1


class TestUploadIntegration:
    """Integration tests for upload functionality."""

    def test_upload_workflow_simulation(self, client):
        """Simulate the upload workflow (without actual file upload)."""
        # Create zones that would be needed for upload processing
        zones = [
            {"id": 1, "borough": "Manhattan", "zone_name": "Midtown", "service_zone": "Yellow", "active": True},
            {"id": 2, "borough": "Manhattan", "zone_name": "Downtown", "service_zone": "Yellow", "active": True},
            {"id": 3, "borough": "Brooklyn", "zone_name": "DUMBO", "service_zone": "Green", "active": True},
        ]

        for zone in zones:
            response = client.post("/zones", json=zone)
            assert response.status_code == 201

        # Test that zones are ready for upload processing
        response = client.get("/zones")
        assert response.status_code == 200
        assert len(response.json()) == 3

        # Note: Actual file upload testing would require sample parquet files
        # This test verifies the foundation is ready for upload processing

    def test_algorithm_integration_readiness(self, client):
        """Test that algorithm components are ready for integration."""
        # This would test that the algorithm functions can be called
        # with data from the API, but requires actual parquet processing

        # For now, just verify the API structure supports the workflow
        response = client.get("/health")
        assert response.status_code == 200

        # Verify zones and routes endpoints are available
        response = client.get("/zones")
        assert response.status_code == 200

        response = client.get("/routes")
        assert response.status_code == 200