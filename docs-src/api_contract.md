# API Contract Documentation

## Overview

This document defines the complete API contract for the Demand Prediction Service. The API provides CRUD operations for Zones and Routes, along with parquet file upload capabilities for NYC TLC trip data processing.

**Base URL**: `http://localhost:8000`

**API Version**: 1.0.0

## General Conventions

### HTTP Methods

-   **GET**: Retrieve resources
-   **POST**: Create new resources
-   **PUT**: Update existing resources
-   **DELETE**: Remove resources

### Response Codes

-   **200 OK**: Successful GET, PUT, or POST with response body
-   **201 Created**: Successful POST creating a new resource
-   **204 No Content**: Successful DELETE
-   **400 Bad Request**: Business rule violation or custom validation error
-   **404 Not Found**: Resource not found
-   **422 Unprocessable Entity**: Pydantic validation error

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

For validation errors (422):

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Health Check

### Get API Health Status

**Endpoint**: `GET /health`

**Description**: Check if the API is running and healthy.

**Tags**: `Health`

**Request**: None

**Response** (200):

```json
{
  "status": "ok"
}
```

## Zones

Zones represent NYC TLC Location IDs with geographic information.

### Zone Schema

**Fields**:

-   `id` (integer, required): TLC LocationID, must be positive
-   `borough` (string, required): Borough name, not empty
-   `zone_name` (string, required): Zone name, not empty
-   `service_zone` (string, required): Service zone designation
-   `active` (boolean, required): Whether zone is active
-   `created_at` (datetime, auto-generated): Timestamp of creation

<details>
<summary>Explanation of fields</summary>
**Borough:** A borough is a primary administrative division of New York City. NYC is composed of five boroughs: **Manhattan, Brooklyn, Queens, The Bronx, and Staten Island**. In the context of the TLC dataset, there is often a sixth "borough" designated as **EWR** (Newark Airport) or **Unknown**. In your schema, this field serves to categorize the specific `LocationID` into its respective geographic region of the city.

**NYC TLC Location IDs:** These are unique numerical identifiers (ranging from 1 to 265) assigned by the **Taxi and Limousine Commission** to specific "Taxi Zones." Instead of using precise GPS coordinates (Latitude/Longitude) for every trip—which would be data-heavy and privacy-invasive—the TLC aggregates pickup and drop-off locations into these predefined zones. This makes it easier to analyze patterns like "trips from the Upper East Side to JFK Airport."

**Geographic Information Bundled:** While your specific schema only lists `id` and `borough`, the official TLC "Zone" concept typically bundles the following geographic data:

-   **Zone Name:** The neighborhood name (e.g., "Times Square/Theatre District", "Astoria", "East Village").
-   **Service Zone:** Categories like **Yellow Zone** (primarily Manhattan), **Boro Zone** (outer boroughs where Green Taxis operate), or **Airports**.
-   **Geometry (Shapefiles):** Behind the scenes, each ID corresponds to a specific polygon on a map. This allows systems to determine exactly which streets and boundaries fall within `LocationID: 142`.

</details>

**Validation Rules**:

-   `id` must be > 0
-   `zone_name` must not be empty
-   `borough` must not be empty

### Create Zone

**Endpoint**: `POST /zones`

**Tags**: `Zones`

**Request Body**:

```json
{
  "id": 1,
  "borough": "Manhattan",
  "zone_name": "Newark Airport",
  "service_zone": "EWR",
  "active": true
}
```

**Response** (201):

```json
{
  "id": 1,
  "borough": "Manhattan",
  "zone_name": "Newark Airport",
  "service_zone": "EWR",
  "active": true,
  "created_at": "2025-01-25T20:00:00Z"
}
```

**Error Responses**:

-   400: ID not positive, zone_name empty, or borough empty
-   422: Missing required fields or invalid data types

### List Zones

**Endpoint**: `GET /zones`

**Tags**: `Zones`

**Query Parameters** (all optional):

-   `active` (boolean): Filter by active status
-   `borough` (string): Filter by borough name

**Request**: `GET /zones?active=true&borough=Manhattan`

**Response** (200):

```json
[
  {
    "id": 1,
    "borough": "Manhattan",
    "zone_name": "Newark Airport",
    "service_zone": "EWR",
    "active": true,
    "created_at": "2025-01-25T20:00:00Z"
  },
  {
    "id": 2,
    "borough": "Manhattan",
    "zone_name": "Jamaica Bay",
    "service_zone": "Boro Zone",
    "active": true,
    "created_at": "2025-01-25T20:05:00Z"
  }
]
```

### Get Zone by ID

**Endpoint**: `GET /zones/{id}`

**Tags**: `Zones`

**Path Parameters**:

-   `id` (integer): Zone ID

**Request**: `GET /zones/1`

**Response** (200):

```json
{
  "id": 1,
  "borough": "Manhattan",
  "zone_name": "Newark Airport",
  "service_zone": "EWR",
  "active": true,
  "created_at": "2025-01-25T20:00:00Z"
}
```

**Error Responses**:

-   404: Zone with specified ID not found

### Update Zone

**Endpoint**: `PUT /zones/{id}`

**Tags**: `Zones`

**Path Parameters**:

-   `id` (integer): Zone ID

**Request Body**:

```json
{
  "id": 1,
  "borough": "Manhattan",
  "zone_name": "Newark Airport - Updated",
  "service_zone": "EWR",
  "active": false
}
```

**Response** (200):

```json
{
  "id": 1,
  "borough": "Manhattan",
  "zone_name": "Newark Airport - Updated",
  "service_zone": "EWR",
  "active": false,
  "created_at": "2025-01-25T20:00:00Z"
}
```

**Error Responses**:

-   400: Validation errors (empty fields, invalid ID)
-   404: Zone with specified ID not found

### Delete Zone

**Endpoint**: `DELETE /zones/{id}`

**Tags**: `Zones`

**Path Parameters**:

-   `id` (integer): Zone ID

**Request**: `DELETE /zones/1`

**Response** (204): No content

**Error Responses**:

-   404: Zone with specified ID not found

## Routes

Routes represent pickup-dropoff zone pairs with validation rules.

### Route Schema

**Fields**:

-   `id` (integer or uuid, required): Route identifier
-   `pickup_zone_id` (integer, required): Reference to Zone.id for pickup
-   `dropoff_zone_id` (integer, required): Reference to Zone.id for dropoff
-   `name` (string, required): Route name, not empty
-   `active` (boolean, required): Whether route is active
-   `created_at` (datetime, auto-generated): Timestamp of creation

**Validation Rules**:

-   `pickup_zone_id` must be > 0
-   `dropoff_zone_id` must be > 0
-   `pickup_zone_id` != `dropoff_zone_id` (returns 400 if equal)
-   `name` must not be empty
-   Both pickup and dropoff zones must exist (returns 400 if not found)

### Create Route

**Endpoint**: `POST /routes`

**Tags**: `Routes`

**Request Body**:

```json
{
  "pickup_zone_id": 1,
  "dropoff_zone_id": 2,
  "name": "Manhattan to JFK",
  "active": true
}
```

**Response** (201):

```json
{
  "id": 1,
  "pickup_zone_id": 1,
  "dropoff_zone_id": 2,
  "name": "Manhattan to JFK",
  "active": true,
  "created_at": "2025-01-25T20:10:00Z"
}
```

**Error Responses**:

-   400: pickup_zone_id == dropoff_zone_id, zones don't exist, or IDs not positive
-   422: Missing required fields or invalid data types

### List Routes

**Endpoint**: `GET /routes`

**Tags**: `Routes`

**Query Parameters** (all optional):

-   `active` (boolean): Filter by active status
-   `pickup_zone_id` (integer): Filter by pickup zone ID
-   `dropoff_zone_id` (integer): Filter by dropoff zone ID

**Request**: `GET /routes?active=true&pickup_zone_id=1`

**Response** (200):

```json
[
  {
    "id": 1,
    "pickup_zone_id": 1,
    "dropoff_zone_id": 2,
    "name": "Manhattan to JFK",
    "active": true,
    "created_at": "2025-01-25T20:10:00Z"
  },
  {
    "id": 2,
    "pickup_zone_id": 1,
    "dropoff_zone_id": 3,
    "name": "Manhattan to LaGuardia",
    "active": true,
    "created_at": "2025-01-25T20:15:00Z"
  }
]
```

### Get Route by ID

**Endpoint**: `GET /routes/{id}`

**Tags**: `Routes`

**Path Parameters**:

-   `id` (integer): Route ID

**Request**: `GET /routes/1`

**Response** (200):

```json
{
  "id": 1,
  "pickup_zone_id": 1,
  "dropoff_zone_id": 2,
  "name": "Manhattan to JFK",
  "active": true,
  "created_at": "2025-01-25T20:10:00Z"
}
```

**Error Responses**:

-   404: Route with specified ID not found

### Update Route

**Endpoint**: `PUT /routes/{id}`

**Tags**: `Routes`

**Path Parameters**:

-   `id` (integer): Route ID

**Request Body**:

```json
{
  "pickup_zone_id": 1,
  "dropoff_zone_id": 2,
  "name": "Manhattan to JFK - Express",
  "active": false
}
```

**Response** (200):

```json
{
  "id": 1,
  "pickup_zone_id": 1,
  "dropoff_zone_id": 2,
  "name": "Manhattan to JFK - Express",
  "active": false,
  "created_at": "2025-01-25T20:10:00Z"
}
```

**Error Responses**:

-   400: pickup_zone_id == dropoff_zone_id or zones don't exist
-   404: Route with specified ID not found

### Delete Route

**Endpoint**: `DELETE /routes/{id}`

**Tags**: `Routes`

**Path Parameters**:

-   `id` (integer): Route ID

**Request**: `DELETE /routes/1`

**Response** (204): No content

**Error Responses**:

-   404: Route with specified ID not found

## Uploads

Upload and process NYC TLC trip data parquet files.

### Upload Parquet File

**Endpoint**: `POST /uploads/trips-parquet`

**Tags**: `Uploads`

**Content Type**: `multipart/form-data`

**Form Parameters**:

-   `file` (file, required): Parquet file to upload
-   `mode` (string, required): Processing mode - "create" or "update"
-   `limit_rows` (integer, optional): Maximum rows to process (default: 50000)
-   `top_n_routes` (integer, optional): Number of top routes to process (default: 50)

**Request**:

```
POST /uploads/trips-parquet
Content-Type: multipart/form-data

file: yellow_tripdata_2024-01.parquet
mode: create
limit_rows: 50000
top_n_routes: 50
```

**Response** (200):

```json
{
  "file_name": "yellow_tripdata_2024-01.parquet",
  "rows_read": 50000,
  "zones_created": 0,
  "zones_updated": 0,
  "routes_detected": 120,
  "routes_created": 80,
  "routes_updated": 40,
  "errors": []
}
```

**Error Response with Errors**:

```json
{
  "file_name": "yellow_tripdata_2024-01.parquet",
  "rows_read": 50000,
  "zones_created": 5,
  "zones_updated": 10,
  "routes_detected": 120,
  "routes_created": 75,
  "routes_updated": 40,
  "errors": [
    "Route with pickup=1 dropoff=1 failed: pickup and dropoff cannot be equal",
    "Zone with id=999 not found during route creation"
  ]
}
```

**Processing Logic**:

1.  Read parquet file using pandas
2.  Apply `limit_rows` to prevent memory issues
3.  Compute (PULocationID, DOLocationID) pairs with counts
4.  Select top N routes by frequency
5.  For each top route:

-   Check if zones exist, create with defaults if missing
-   Check if route exists via GET /routes?pickup_zone_id=X&dropoff_zone_id=Y
-   If not exists: POST /routes
-   If exists and mode="update": PUT /routes/{id}

**Required Columns**:

-   `PULocationID`: Pickup location ID
-   `DOLocationID`: Dropoff location ID

**Error Responses**:

-   400: Missing required columns (PULocationID, DOLocationID)
-   400: Invalid mode (must be "create" or "update")
-   422: Invalid file format or parameters

## Data Models Summary

### Zone Model

```python
{
  "id": int,              # > 0, required
  "borough": str,         # not empty, required
  "zone_name": str,       # not empty, required
  "service_zone": str,    # required
  "active": bool,         # required
  "created_at": datetime  # auto-generated
}
```

### Route Model

```python
{
  "id": int | uuid,           # required
  "pickup_zone_id": int,      # > 0, required, must exist in zones
  "dropoff_zone_id": int,     # > 0, required, must exist in zones, != pickup
  "name": str,                # not empty, required
  "active": bool,             # required
  "created_at": datetime      # auto-generated
}
```

### Upload Response Model

```python
{
  "file_name": str,
  "rows_read": int,
  "zones_created": int,
  "zones_updated": int,
  "routes_detected": int,
  "routes_created": int,
  "routes_updated": int,
  "errors": List[str]
}
```

## Implementation Dependencies

### Zones Endpoints (#10)

-   **Depends on**: Issue #6 (Pydantic Schemas - Nico Naran)
-   **Enables**: Routes endpoints, Upload endpoints

### Routes Endpoints (#11)

-   **Depends on**: Issue #6 (Pydantic Schemas - Nico Naran), Issue #10 (Zones)
-   **Enables**: Upload endpoints

### Upload Endpoints (#12)

-   **Depends on**:
    -   Issue #6 (Pydantic Schemas - Nico Naran)
    -   Issue #7 (Parquet Storage Layer - Nico Naran)
    -   Issue #8 (Route Optimization Algorithm - Nico Naran)
    -   Issue #9 (Integrate Algorithm - Nico Naran)
    -   Issue #10 (Zones Endpoints)
    -   Issue #11 (Routes Endpoints)

## Testing Checklist

Minimum 8 API tests recommended:

**Zones**:

-   [ ] Create zone successfully
-   [ ] List zones with filters
-   [ ] Get zone by ID (404 for non-existent)
-   [ ] Update zone successfully
-   [ ] Delete zone successfully

**Routes**:

-   [ ] Create route successfully
-   [ ] Validation: pickup_zone_id == dropoff_zone_id returns 400
-   [ ] Update route (404 for non-existent)

**Upload**:

-   [ ] Upload parquet returns summary
-   [ ] Loaded items appear in list endpoints

## Frontend Integration Notes

**API URL Configuration**:

-   Docker Compose: `http://api:8000`
-   Local Development: `http://localhost:8000`

**CORS**:

-   Enabled for all origins in development
-   Frontend can make requests from any origin

**Authentication**:

-   Not required for MVP (PSET #1)
-   To be added in future iterations
