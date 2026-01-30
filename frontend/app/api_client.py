"""Simple HTTP client for the FastAPI backend.

This module centralizes access to the backend API so that
Streamlit pages can reuse the same configuration and error
handling.
"""

import os
from typing import Any, Dict

import requests


def get_api_url() -> str:
    """Return the base URL for the backend API.

    Reads the value from the API_URL environment variable,
    defaulting to http://localhost:8000 for local development.
    """

    return os.getenv("API_URL", "http://localhost:8000").rstrip("/")


def get_health() -> Dict[str, Any]:
    """Call the /health endpoint and return its JSON response.

    Raises requests.RequestException if the request fails
    or if the status code is not successful.
    """

    base_url = get_api_url()
    response = requests.get(f"{base_url}/health", timeout=5)
    response.raise_for_status()
    return response.json()
