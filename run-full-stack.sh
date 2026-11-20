#!/bin/bash

# Construction Hazard AI - Full Stack Startup Script
# This script starts both the Python FastAPI backend and React frontend

set -e

echo "🏗️  Construction Safety AI - Full Stack Startup"
echo "================================================="
echo ""

# Check if running from correct directory
if [ ! -f "backend.py" ]; then
    echo "❌ Error: backend.py not found. Please run this script from the project root."
    exit 1
fi

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Step 1: Starting Python FastAPI Backend...${NC}"
echo "API will run at: http://localhost:8000"
python -m uvicorn backend:app --reload &
BACKEND_PID=$!
sleep 3

echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
echo ""

echo -e "${YELLOW}Step 2: Starting React Frontend...${NC}"
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

echo "Frontend will run at: http://localhost:3000"
npm run dev &
FRONTEND_PID=$!
sleep 3

cd ..

echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
echo ""

echo -e "${GREEN}✅ Full Stack Application Started!${NC}"
echo ""
echo "🌐 Open your browser and navigate to: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both services..."
echo ""

# Keep script running
wait

# Cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
