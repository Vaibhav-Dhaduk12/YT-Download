#!/usr/bin/env bash
set -euo pipefail

echo "Running backend tests..."
cd backend
poetry run pytest --cov=app --cov-report=term-missing
cd ..

echo "All tests passed!"
