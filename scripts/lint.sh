#!/usr/bin/env bash
set -euo pipefail

echo "Running backend linters..."
cd backend
poetry run ruff check app/
poetry run black --check app/
echo "Linting passed!"
cd ..
