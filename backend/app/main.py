"""
FastAPI main application for Demand Prediction Service.

This module creates the FastAPI application instance and wires up
all route modules for zones, routes, and uploads.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Router imports will be implemented in subsequent issues
# from app import routes_zones, routes_routes, routes_uploads

app = FastAPI(
    title="Demand Prediction Service",
    description="NYC TLC Zones and Routes Management System",
    version="1.0.0",
)

# CORS middleware to allow Streamlit frontend to communicate with API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify API is running.

    Returns:
        dict: Status message indicating API health
    """
    return {"status": "ok"}


# Routers will be included here in subsequent issues:
# app.include_router(routes_zones.router, prefix="/zones", tags=["Zones"])
# app.include_router(routes_routes.router, prefix="/routes", tags=["Routes"])
# app.include_router(routes_uploads.router, prefix="/uploads", tags=["Uploads"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
