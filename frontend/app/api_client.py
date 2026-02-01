"""Simple HTTP client for the FastAPI backend.

This module centralizes access to the backend API so that Streamlit pages can
reuse the same configuration and error handling.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import requests


@dataclass(frozen=True)
class ApiError(Exception):
    """Raised when the backend returns a non-success response."""

    status_code: int
    detail: Any

    def __str__(self) -> str:
        return f"API error {self.status_code}: {self.detail}"


def get_api_url() -> str:
    """Return the base URL for the backend API.

    Reads the value from the API_URL environment variable, defaulting to
    http://localhost:8000 for local development.
    """

    return os.getenv("API_URL", "http://localhost:8000").rstrip("/")


def _request(
    method: str,
    path: str,
    *,
    params: dict[str, Any] | None = None,
    json: dict[str, Any] | None = None,
    timeout_seconds: int = 10,
) -> Any:
    """Perform an HTTP request to the backend API.

    Args:
        method: HTTP method.
        path: API path, starting with '/'.
        params: Optional query parameters.
        json: Optional JSON body.
        timeout_seconds: Request timeout.

    Returns:
        Parsed JSON response, or None for empty responses.

    Raises:
        ApiError: If the API returns a non-success status code.
        requests.RequestException: For connection/timeout errors.
    """

    base_url = get_api_url()
    url = f"{base_url}{path}"

    response = requests.request(
        method=method,
        url=url,
        params=params,
        json=json,
        timeout=timeout_seconds,
    )

    if response.ok:
        if not response.content:
            return None
        return response.json()

    try:
        detail: Any = response.json().get("detail")
    except Exception:  # noqa: BLE001
        detail = response.text

    raise ApiError(status_code=response.status_code, detail=detail)


def get_health() -> dict[str, Any]:
    """Call the /health endpoint and return its JSON response."""

    return _request("GET", "/health", timeout_seconds=5)


def list_zones(
    *,
    active: bool | None = None,
    borough: str | None = None,
) -> list[dict[str, Any]]:
    """List zones with optional filters."""

    params: dict[str, Any] = {}
    if active is not None:
        params["active"] = active
    if borough:
        params["borough"] = borough
    return _request("GET", "/zones", params=params)


def get_zone(zone_id: int) -> dict[str, Any]:
    """Get a zone by id."""

    return _request("GET", f"/zones/{zone_id}")


def create_zone(payload: dict[str, Any]) -> dict[str, Any]:
    """Create a zone."""

    return _request("POST", "/zones", json=payload)


def update_zone(zone_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    """Update a zone by id."""

    return _request("PUT", f"/zones/{zone_id}", json=payload)


def delete_zone(zone_id: int) -> None:
    """Delete a zone by id."""

    _request("DELETE", f"/zones/{zone_id}")


def list_routes(
    *,
    active: bool | None = None,
    pickup_zone_id: int | None = None,
    dropoff_zone_id: int | None = None,
) -> list[dict[str, Any]]:
    """List routes with optional filters."""

    params: dict[str, Any] = {}
    if active is not None:
        params["active"] = active
    if pickup_zone_id is not None:
        params["pickup_zone_id"] = pickup_zone_id
    if dropoff_zone_id is not None:
        params["dropoff_zone_id"] = dropoff_zone_id
    return _request("GET", "/routes", params=params)


def get_route(route_id: int) -> dict[str, Any]:
    """Get a route by id."""

    return _request("GET", f"/routes/{route_id}")


def create_route(payload: dict[str, Any]) -> dict[str, Any]:
    """Create a route."""

    return _request("POST", "/routes", json=payload)


def update_route(route_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    """Update a route by id."""

    return _request("PUT", f"/routes/{route_id}", json=payload)


def delete_route(route_id: int) -> None:
    """Delete a route by id."""

    _request("DELETE", f"/routes/{route_id}")
