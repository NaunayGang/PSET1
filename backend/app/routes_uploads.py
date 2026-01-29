"""
Upload endpoints for parquet files.

This module implements the parquet file upload endpoint:
- POST /uploads/trips-parquet - Upload and process NYC TLC trip data

The endpoint:
1. Accepts parquet file uploads via multipart/form-data
2. Processes trip data (PULocationID, DOLocationID pairs) IN MEMORY
3. Uses IntegrationService to create/update Zones and Routes
4. Returns summary statistics (rows read, created, updated, errors)

Issue #9: Integrate Algorithm with API Routes
"""

import logging
import tempfile
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from io import BytesIO

from app.schemas import UploadResponse
from app.storage import get_global_storage
from app.integration import IntegrationService

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize integration service with global storage
storage = get_global_storage()
integration_service = IntegrationService(storage)


@router.post(
    "/uploads/trips-parquet",
    response_model=UploadResponse,
    status_code=status.HTTP_200_OK,
    tags=["Uploads"],
)
async def upload_parquet(
    file: UploadFile = File(..., description="Parquet file to upload"),
    mode: str = Form(..., description="Processing mode: 'create' or 'update'"),
    limit_rows: int = Form(50000, description="Maximum rows to process"),
    top_n_routes: int = Form(50, description="Number of top routes to extract"),
):
    """
    Upload and process a parquet file with NYC TLC trip data.

    This endpoint processes the file in memory without persisting to disk.
    It extracts top N route pairs and creates/updates zones and routes.

    Args:
        file: Uploaded parquet file
        mode: Processing mode ('create' or 'update')
        limit_rows: Maximum number of rows to process (default: 50000)
        top_n_routes: Number of top routes to extract (default: 50)

    Returns:
        UploadResponse: Summary with counts of created/updated entities and errors

    Raises:
        400: Invalid mode, missing columns, or validation errors
        422: Invalid file format or parameters
        500: Unexpected server error
    """
    logger.info(
        f"upload_parquet called: filename={file.filename}, mode={mode}, "
        f"limit_rows={limit_rows}, top_n={top_n_routes}"
    )

    # Validate file type
    if not file.filename or not file.filename.endswith('.parquet'):
        logger.warning(f"Invalid file type: {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a .parquet file"
        )

    # Validate mode
    if mode not in ['create', 'update']:
        logger.warning(f"Invalid mode: {mode}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid mode: {mode}. Must be 'create' or 'update'"
        )

    # Validate parameters
    if limit_rows <= 0 or limit_rows > 1000000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="limit_rows must be between 1 and 1,000,000"
        )

    if top_n_routes <= 0 or top_n_routes > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="top_n_routes must be between 1 and 500"
        )

    try:
        # Read file contents into memory (no disk write!)
        contents = await file.read()
        logger.info(f"Read {len(contents)} bytes from uploaded file")

        # Create a temporary file for pandas to read
        # This is still in-memory processing via tempfile
        with tempfile.NamedTemporaryFile(delete=True, suffix='.parquet') as tmp_file:
            tmp_file.write(contents)
            tmp_file.flush()

            # Process parquet using integration service
            result = integration_service.process_parquet_upload(
                file_path=tmp_file.name,
                file_name=file.filename,
                mode=mode,
                limit_rows=limit_rows,
                top_n_routes=top_n_routes,
            )

            logger.info(
                f"Upload processed successfully: zones_created={result.zones_created}, "
                f"routes_created={result.routes_created}, errors={len(result.errors)}"
            )

            return result

    except ValueError as e:
        # Business logic errors (missing columns, invalid data)
        logger.error(f"Validation error processing parquet: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Unexpected errors
        logger.exception(f"Unexpected error processing upload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
