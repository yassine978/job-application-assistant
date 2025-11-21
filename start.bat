@echo off
REM Job Application Assistant - Quick Start Script for Windows
REM This script helps you start the application quickly

echo ==================================================
echo   Job Application Assistant - Quick Start
echo ==================================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo [OK] Docker is running

REM Check if .env file exists
if not exist .env (
    echo.
    echo [WARNING] .env file not found!
    echo Creating .env from .env.example...
    copy .env.example .env >nul
    echo.
    echo [ACTION REQUIRED] Please edit .env file and add your API keys:
    echo   - GROQ_API_KEY
    echo   - ADZUNA_APP_ID
    echo   - ADZUNA_API_KEY
    echo.
    echo Then run this script again.
    pause
    exit /b 1
)

echo [OK] .env file exists

REM Check if API keys are set (basic check)
findstr /C:"your_groq_api_key_here" .env >nul
if not errorlevel 1 (
    echo.
    echo [WARNING] API keys appear to be default placeholders!
    echo Please edit .env file with your actual API keys.
    echo.
    set /p CONTINUE="Continue anyway? (y/N): "
    if /i not "%CONTINUE%"=="y" exit /b 1
)

echo.
echo [*] Starting services...
echo This may take a few minutes on first run (downloading images)...
echo.

REM Start services
docker-compose up -d

echo.
echo [*] Waiting for services to be ready...
timeout /t 5 /nobreak >nul

REM Check if services are running
docker-compose ps | findstr "Up" >nul
if not errorlevel 1 (
    echo [OK] Services are running!
    echo.
    echo ==================================================
    echo   Application is ready!
    echo ==================================================
    echo.
    echo Open your browser and go to:
    echo.
    echo     http://localhost:8501
    echo.
    echo To view logs:
    echo     docker-compose logs -f app
    echo.
    echo To stop services:
    echo     docker-compose down
    echo.
    echo ==================================================
    echo.

    REM Try to open browser
    start http://localhost:8501
) else (
    echo [ERROR] Services failed to start!
    echo Check logs with: docker-compose logs
    pause
    exit /b 1
)

pause
