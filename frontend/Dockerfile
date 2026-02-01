# Frontend Dockerfile for Streamlit Demand Prediction UI
# Multi-stage build for optimized production image with excellent layer caching

# =============================================================================
# Stage 1: Builder - Install dependencies
# =============================================================================
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies if needed
# Keep layer minimal and cached
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        && \
    rm -rf /var/lib/apt/lists/*

# Copy ONLY requirements first (layer caching optimization)
# This layer only rebuilds when requirements.txt changes
COPY requirements.txt .

# Install Python dependencies to user directory
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
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
# This layer rebuilds whenever code changes
COPY --chown=appuser:appuser app/ ./app/

# Set environment variables
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER appuser

# Expose Streamlit port
EXPOSE 8501

# Health check to verify Streamlit is responding
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

# Run Streamlit
# --server.port 8501: Default Streamlit port
# --server.address 0.0.0.0: Listen on all interfaces (required for Docker)
# --server.headless true: Run without browser
# --server.fileWatcherType none: Disable file watching in production
CMD ["streamlit", "run", "app/Home.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.fileWatcherType=none"]
