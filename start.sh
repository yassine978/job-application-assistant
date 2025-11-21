#!/bin/bash

# Job Application Assistant - Quick Start Script
# This script helps you start the application quickly

set -e

echo "=================================================="
echo "  Job Application Assistant - Quick Start"
echo "=================================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "[ERROR] Docker is not running!"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

echo "[OK] Docker is running"

# Check if .env file exists
if [ ! -f .env ]; then
    echo ""
    echo "[WARNING] .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "[ACTION REQUIRED] Please edit .env file and add your API keys:"
    echo "  - GROQ_API_KEY"
    echo "  - ADZUNA_APP_ID"
    echo "  - ADZUNA_API_KEY"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo "[OK] .env file exists"

# Check if API keys are set
if grep -q "your_groq_api_key_here" .env || grep -q "your_adzuna_app_id_here" .env; then
    echo ""
    echo "[WARNING] API keys appear to be default placeholders!"
    echo "Please edit .env file with your actual API keys."
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "[*] Starting services..."
echo "This may take a few minutes on first run (downloading images)..."
echo ""

# Start services
docker-compose up -d

echo ""
echo "[*] Waiting for services to be ready..."
sleep 5

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "[OK] Services are running!"
    echo ""
    echo "=================================================="
    echo "  Application is ready!"
    echo "=================================================="
    echo ""
    echo "Open your browser and go to:"
    echo ""
    echo "    http://localhost:8501"
    echo ""
    echo "To view logs:"
    echo "    docker-compose logs -f app"
    echo ""
    echo "To stop services:"
    echo "    docker-compose down"
    echo ""
    echo "=================================================="
    echo ""

    # Try to open browser (works on some systems)
    if command -v xdg-open > /dev/null; then
        xdg-open http://localhost:8501 2>/dev/null || true
    elif command -v open > /dev/null; then
        open http://localhost:8501 2>/dev/null || true
    fi
else
    echo "[ERROR] Services failed to start!"
    echo "Check logs with: docker-compose logs"
    exit 1
fi
