#!/bin/bash
# Start PoisonSense-AI Application
# Run this script to start both backend and frontend

echo "🚀 Starting PoisonSense-AI Application"
echo "======================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Function to cleanup background processes on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM

# Start Backend
echo -e "\n${BLUE}Starting Backend Server...${NC}"
cd "$SCRIPT_DIR/backend"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install dependencies if needed
if [ ! -f ".deps_installed" ]; then
    echo "Installing backend dependencies..."
    pip install -r requirements.txt -q
    touch .deps_installed
fi

# Initialize database
echo "Initializing database..."
python -c "from app.db.init_db import init_database; init_database()" 2>/dev/null || true

# Start uvicorn in background
echo -e "${GREEN}✓ Starting backend on http://localhost:8000${NC}"
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start Frontend
echo -e "\n${BLUE}Starting Frontend Server...${NC}"
cd "$SCRIPT_DIR/frontend"

# Install npm dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

echo -e "${GREEN}✓ Starting frontend on http://localhost:5173${NC}"
npm run dev &
FRONTEND_PID=$!

# Wait a bit for frontend to start
sleep 3

echo ""
echo "======================================="
echo -e "${GREEN}🎉 PoisonSense-AI is running!${NC}"
echo "======================================="
echo ""
echo "📍 Frontend:  http://localhost:5173"
echo "📍 Backend:   http://localhost:8000"
echo "📍 API Docs:  http://localhost:8000/docs"
echo ""
echo "🔐 Test Login Credentials:"
echo "   Email:    admin@poisonsense.ai"
echo "   Password: admin123"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
