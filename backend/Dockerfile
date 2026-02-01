# Backend Dockerfile for FastAPI Demand Prediction Service
# Multi-stage build for optimized production image with excellent layer caching

# =============================================================================
# Stage 1: Builder - Install dependencies
# =============================================================================
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies needed for building Python packages
# Combine RUN commands to reduce layers and leverage cache
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        && \
    rm -rf /var/lib/apt/lists/*

# Copy ONLY requirements first (layer caching optimization)
# This layer only rebuilds when requirements.txt changes
COPY requirements.txt .

# Install Python dependencies to user directory
# --user flag installs to ~/.local which we'll copy to final stage
RUN pip install --no-cache-dir --user -r requirements.txt

# =============================================================================
# Stage 2: Runtime - Minimal production image
# =============================================================================
FROM python:3.11-slim

WORKDIR /app

# Create non-root user for security best practices
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy Python dependencies from builder stage
# This contains all installed packages
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
# This layer rebuilds whenever code changes
COPY --chown=appuser:appuser app/ ./app/

# Set environment variables
ENV PATH=/home/appuser/.local/bin:$PATH \
    # Forces real-time log output by disabling Python's internal terminal buffering
    PYTHONUNBUFFERED=1 \
    # Prevents Python from creating __pycache__ folders to keep the container clean
    PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER appuser

# Expose FastAPI port
EXPOSE 8000

# Health check to verify API is responding
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run FastAPI with uvicorn
# --host 0.0.0.0: Listen on all interfaces (required for Docker)
# --port 8000: Default FastAPI port
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
