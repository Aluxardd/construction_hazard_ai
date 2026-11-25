#!/bin/bash

# Construction Safety AI - Full Stack Startup Script
# Starts both the Python FastAPI backend and React frontend.

set -e

echo "Construction Safety AI - Full Stack Startup"
echo "==========================================="
echo ""

if [ ! -f "backend.py" ]; then
    echo "Error: backend.py not found. Please run this script from the project root."
    exit 1
fi

PYTHON_BIN="python3"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    PYTHON_BIN="python"
fi

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    echo "Error: python3/python not found in PATH."
    exit 1
fi

BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
    if [ -n "$BACKEND_PID" ]; then
        kill "$BACKEND_PID" 2>/dev/null || true
    fi
    if [ -n "$FRONTEND_PID" ]; then
        kill "$FRONTEND_PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM

echo "Step 1: Starting Python FastAPI Backend at http://localhost:8000 ..."
"$PYTHON_BIN" -m uvicorn backend:app --reload &
BACKEND_PID=$!
sleep 2

echo "Step 2: Starting React Frontend at http://localhost:3000 ..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "Full Stack Application Started!"
echo "Open your browser at: http://localhost:3000"
echo "Press Ctrl+C to stop both services..."
echo ""

wait
