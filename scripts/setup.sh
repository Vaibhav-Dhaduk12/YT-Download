#!/usr/bin/env bash
set -euo pipefail

echo "Setting up YT-Download project..."

# Backend
cd backend
cp -n .env.example .env || true
pip install poetry
poetry install
echo "Backend dependencies installed."
cd ..

# Frontend
cd frontend
npm install
echo "Frontend dependencies installed."
cd ..

echo "Setup complete! Run './scripts/dev-start.sh' to start development."
