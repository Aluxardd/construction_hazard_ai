@echo off
REM Construction Hazard AI - Full Stack Startup Script (Windows)
REM This script starts both the Python FastAPI backend and React frontend

setlocal enabledelayedexpansion
set "PROJECT_ROOT=%cd%"

echo.
echo =========================================================
echo 🏗️  Construction Safety AI - Full Stack Startup
echo =========================================================
echo.

REM Check if running from correct directory
if not exist "backend.py" (
    echo ❌ Error: backend.py not found. Please run this script from the project root.
    pause
    exit /b 1
)

echo [1/4] Starting Python FastAPI Backend...
echo API will run at: http://localhost:8000
echo.

start "Construction Hazard AI - Backend" python -m uvicorn backend:app --reload
timeout /t 3 /nobreak

echo ✓ Backend started
echo.

echo [2/4] Checking Node.js installation...
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Error: Node.js not found. Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo ✓ Node.js found
echo.

echo [3/4] Starting React Frontend...
cd frontend

if not exist "node_modules" (
    echo Installing dependencies... this may take a minute
    call npm install
    if %errorlevel% neq 0 (
        echo ❌ Error: npm install failed
        pause
        exit /b 1
    )
)

echo Frontend will run at: http://localhost:3000
echo.

start "Construction Hazard AI - Frontend" npm run dev
timeout /t 3 /nobreak

cd ..

echo [4/4] Verifying services...
timeout /t 2 /nobreak

echo.
echo =========================================================
echo ✅ Full Stack Application Started!
echo =========================================================
echo.
echo 🌐 Open your browser and navigate to:
echo    http://localhost:3000
echo.
echo 📊 Backend API documentation:
echo    http://localhost:8000/docs
echo.
echo Press any key to close this window...
pause
