#!/bin/bash

# ==============================================================================
# AlgoInfluencers Platform Runner
# This script starts both the Next.js frontend and FastAPI backend simultaneously.
# Keep this terminal open to run the servers. Press Ctrl+C to stop both.
# ==============================================================================

echo -e "\033[1;34m==================================================\033[0m"
echo -e "\033[1;36m       🚀 Starting AlgoInfluencers Platform       \033[0m"
echo -e "\033[1;34m==================================================\033[0m"

# Absolute path to the directory containing this script
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to handle shutdown of both background processes
cleanup() {
    echo -e "\n\033[1;31mStopping AlgoInfluencers Platform...\033[0m"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    exit 0
}

# Trap SIGINT (Ctrl+C) and call the cleanup function
trap cleanup SIGINT SIGTERM

# ==============================================================================
# 1. Start the FastAPI Backend (Port 8000)
# ==============================================================================
echo -e "\033[1;33m[1/2] Starting FastAPI Backend...\033[0m"
cd "$PROJECT_ROOT/backend" || exit 1

# Check if virtual environment exists, if not create and install
if [ ! -d ".venv" ]; then
    echo -e "\033[0;32mCreating Python virtual environment...\033[0m"
    python3 -m venv .venv
    source .venv/bin/activate
    echo -e "\033[0;32mInstalling backend dependencies...\033[0m"
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

# Run backend in the background
uvicorn app.main:app --reload --port 8000 --host 0.0.0.0 > ../backend.log 2>&1 &
BACKEND_PID=$!
echo -e "\033[0;32mBackend started (PID: $BACKEND_PID). Logs: backend.log\033[0m"

# ==============================================================================
# 2. Start the Next.js Frontend (Port 3000)
# ==============================================================================
echo -e "\033[1;33m[2/2] Starting Next.js Frontend...\033[0m"
cd "$PROJECT_ROOT/frontend" || exit 1

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo -e "\033[0;32mInstalling frontend dependencies...\033[0m"
    npm install
fi

# Create .env.local if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo -e "\033[0;32mCreating .env.local file...\033[0m"
    echo "NEXT_PUBLIC_API_BASE_URL=http://localhost:8000" > .env.local
fi

# Run frontend in the background
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "\033[0;32mFrontend started (PID: $FRONTEND_PID). Logs: frontend.log\033[0m"

# ==============================================================================
# 3. Ready State
# ==============================================================================
echo -e "\033[1;34m==================================================\033[0m"
echo -e "\033[1;32m✅ Platform is running successfully!\033[0m"
echo -e "   Frontend: \033[1;36mhttp://localhost:3000\033[0m"
echo -e "   Backend:  \033[1;36mhttp://localhost:8000\033[0m"
echo -e "\033[1;34m==================================================\033[0m"
echo -e "\033[0;90mPress Ctrl+C to stop both servers.\033[0m"

# Wait indefinitely while logging output, allows ctrl+c trap to catch
wait
