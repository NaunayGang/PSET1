"""
Integration service connecting storage, algorithm, and API endpoints.

This module implements Issue #9: Integrate Algorithm with API Routes
- Connects parquet processing algorithm with storage layer
- Ensures idempotency for upload operations
- Provides validation and error handling
- Coordinates zone/route creation and updates

Dependencies:
- storage.py (Issue #7 - implemented by Nico Naran)
- algorithm.py (Issue #8 - being implemented by Nico Naran)
- schemas.py (Issue #5/6 - API contract)
"""

import logging
from datetime import datetime
from typing import List, Tuple
import pandas as pd
import pyarrow.parquet as pq

from app.storage import Storage
from app.schemas import ZoneBase, RouteBase, UploadResponse
from app.algorithm import (
    compute_top_routes,
    optimize_route_selection,
    validate_route_pair,
)

logger = logging.getLogger(__name__)


class IntegrationService:
    """
    Service layer integrating storage and algorithm for route optimization.

    This service ensures:
    - Idempotent uploads (same file uploaded twice = same result)
    - Proper zone/route validation
    - Error collection and reporting
    - Atomic-like operations (all-or-nothing per route)
    """

    def __init__(self, storage: Storage):
        """
        Initialize integration service with storage backend.

        Args:
            storage: Storage instance for persisting zones and routes
        """
        self.storage = storage
        logger.info("IntegrationService initialized")

    def process_parquet_upload(
        self,
        file_path: str,
        file_name: str,
        mode: str,
        limit_rows: int = 50000,
        top_n_routes: int = 50,
    ) -> UploadResponse:
        """
        Process uploaded parquet file and create/update zones and routes.

        This is the main integration point for Issue #9, connecting:
        1. Read parquet → compute_top_routes() from algorithm.py
        2. Create missing zones → storage.create_zone()
        3. Create/update routes → storage.create_route() / storage.update_route()

        Args:
            file_path: Path to uploaded parquet file
            file_name: Original filename
            mode: Processing mode ('create' or 'update')
            limit_rows: Maximum rows to process
            top_n_routes: Number of top routes to extract

        Returns:
            UploadResponse: Summary with counts and errors

        Raises:
            ValueError: If mode is invalid or required columns missing
        """
        if mode not in ['create', 'update']:
            raise ValueError(f"Invalid mode: {mode}. Must be 'create' or 'update'")

        logger.info(
            f"Processing parquet upload: file={file_name}, mode={mode}, "
            f"limit_rows={limit_rows}, top_n={top_n_routes}"
        )

        errors = []
        zones_created = 0
        zones_updated = 0
        routes_created = 0
        routes_updated = 0

        try:
            # Step 1: Read parquet file
            df = pd.read_parquet(file_path)
            rows_read = len(df)
            logger.info(f"Read {rows_read} rows from parquet file")

            # Step 2: Compute top routes using algorithm
            top_routes = compute_top_routes(df, limit_rows, top_n_routes)
            routes_detected = len(top_routes)
            logger.info(f"Detected {routes_detected} top routes")

            # Step 3: Get existing routes for idempotency
            existing_routes = {
                (route.pickup_zone_id, route.dropoff_zone_id)
                for route in self.storage.get_all_routes()
            }

            # Step 4: Process each route
            for pickup_zone_id, dropoff_zone_id, frequency in top_routes:
                try:
                    # Validate route pair
                    if not validate_route_pair(pickup_zone_id, dropoff_zone_id):
                        errors.append(
                            f"Invalid route pair: pickup={pickup_zone_id}, "
                            f"dropoff={dropoff_zone_id}"
                        )
                        continue

                    # Ensure zones exist (create with defaults if missing)
                    zone_create_result = self._ensure_zones_exist(
                        pickup_zone_id, dropoff_zone_id, mode
                    )
                    zones_created += zone_create_result['created']
                    zones_updated += zone_create_result['updated']

                    # Create or update route
                    route_result = self._process_route(
                        pickup_zone_id,
                        dropoff_zone_id,
                        frequency,
                        mode,
                        existing_routes,
                    )

                    if route_result['created']:
                        routes_created += 1
                    elif route_result['updated']:
                        routes_updated += 1

                    if route_result.get('error'):
                        errors.append(route_result['error'])

                except Exception as e:
                    error_msg = (
                        f"Error processing route pickup={pickup_zone_id} "
                        f"dropoff={dropoff_zone_id}: {str(e)}"
                    )
                    logger.error(error_msg)
                    errors.append(error_msg)

            logger.info(
                f"Upload complete: zones_created={zones_created}, "
                f"zones_updated={zones_updated}, routes_created={routes_created}, "
                f"routes_updated={routes_updated}, errors={len(errors)}"
            )

            return UploadResponse(
                file_name=file_name,
                rows_read=rows_read,
                zones_created=zones_created,
                zones_updated=zones_updated,
                routes_detected=routes_detected,
                routes_created=routes_created,
                routes_updated=routes_updated,
                errors=errors,
            )

        except ValueError as e:
            # Missing columns or invalid data
            logger.error(f"Parquet validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing parquet: {str(e)}")
            raise

    def _ensure_zones_exist(
        self,
        pickup_zone_id: int,
        dropoff_zone_id: int,
        mode: str,
    ) -> dict:
        """
        Ensure both zones exist, creating them with defaults if necessary.

        Args:
            pickup_zone_id: Pickup zone ID
            dropoff_zone_id: Dropoff zone ID
            mode: Processing mode ('create' or 'update')

        Returns:
            dict with 'created' and 'updated' counts
        """
        created = 0
        updated = 0

        for zone_id in [pickup_zone_id, dropoff_zone_id]:
            if not self.storage.zone_exists(zone_id):
                # Create zone with default values
                zone = ZoneBase(
                    id=zone_id,
                    borough="Unknown",
                    zone_name=f"Zone {zone_id}",
                    service_zone="Unknown",
                    active=True,
                )
                self.storage.create_zone(zone)
                created += 1
                logger.info(f"Created default zone: id={zone_id}")
            elif mode == 'update':
                # Mark existing zone as active
                existing_zone = self.storage.get_zone(zone_id)
                if existing_zone and not existing_zone.active:
                    existing_zone.active = True
                    self.storage.update_zone(existing_zone)
                    updated += 1
                    logger.info(f"Activated zone: id={zone_id}")

        return {'created': created, 'updated': updated}

    def _process_route(
        self,
        pickup_zone_id: int,
        dropoff_zone_id: int,
        frequency: int,
        mode: str,
        existing_routes: set,
    ) -> dict:
        """
        Create or update a route based on mode and existence.

        Implements idempotency guarantee:
        - In 'create' mode: skip if route exists
        - In 'update' mode: update if exists, create if doesn't

        Args:
            pickup_zone_id: Pickup zone ID
            dropoff_zone_id: Dropoff zone ID
            frequency: Trip frequency from parquet data
            mode: Processing mode
            existing_routes: Set of existing (pickup, dropoff) tuples

        Returns:
            dict with 'created', 'updated', and optional 'error' keys
        """
        result = {'created': False, 'updated': False, 'error': None}

        route_pair = (pickup_zone_id, dropoff_zone_id)
        existing_route = self.storage.find_route_by_zones(pickup_zone_id, dropoff_zone_id)

        if existing_route:
            # Route exists
            if mode == 'update':
                # Update the route (mark as active)
                existing_route.active = True
                existing_route.name = f"Route {pickup_zone_id}→{dropoff_zone_id} (freq:{frequency})"
                try:
                    self.storage.update_route(existing_route.id, existing_route)
                    result['updated'] = True
                    logger.info(f"Updated route: id={existing_route.id}")
                except ValueError as e:
                    result['error'] = f"Failed to update route {existing_route.id}: {str(e)}"
            else:
                # Create mode: skip existing route (idempotency)
                logger.debug(f"Skipping existing route: {route_pair}")
        else:
            # Route doesn't exist: create it
            # Generate new route ID using storage method
            new_route_id = self.storage.assing_route_id()

            new_route = RouteBase(
                id=new_route_id,
                pickup_zone_id=pickup_zone_id,
                dropoff_zone_id=dropoff_zone_id,
                name=f"Route {pickup_zone_id}→{dropoff_zone_id} (freq:{frequency})",
                active=True,
            )

            try:
                self.storage.create_route(new_route)
                result['created'] = True
                logger.info(
                    f"Created route: id={new_route_id}, "
                    f"{pickup_zone_id}→{dropoff_zone_id}"
                )
            except ValueError as e:
                result['error'] = f"Failed to create route: {str(e)}"

        return result
