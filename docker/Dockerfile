# Multi-stage build for Job Application Assistant

# Stage 1: Base image with dependencies
FROM python:3.9-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Stage 2: Dependencies
FROM base as dependencies

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Install Playwright and browsers
RUN playwright install-deps && \
    playwright install chromium

# Stage 3: Application
FROM dependencies as application

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p \
    /app/chroma_db \
    /app/generated_documents/cvs \
    /app/generated_documents/cover_letters \
    /app/generated_documents/exports \
    /app/logs

# Set permissions
RUN chmod +x /app/*.py 2>/dev/null || true

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Default command: Run Streamlit dashboard
CMD ["streamlit", "run", "dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]

# Alternative commands (override with docker run):
# - Run tests: docker run app pytest tests/
# - Run scraper: docker run app python -m scrapers.scraper_factory
# - Run shell: docker run -it app /bin/bash
