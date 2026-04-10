#!/usr/bin/env bash
set -euo pipefail

echo "Starting development environment..."

# Start backend in background
cd backend
poetry run uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Start frontend
cd frontend
ng serve &
FRONTEND_PID=$!
cd ..

echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:4200"
echo "API Docs: http://localhost:8000/docs"

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
