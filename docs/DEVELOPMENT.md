# Development Setup

## Prerequisites

- Python 3.11+
- Node.js 18+
- Poetry (`pip install poetry`)
- Angular CLI (`npm install -g @angular/cli`)

## Backend Setup

```bash
cd backend

# Install dependencies
poetry install

# Copy env file
cp .env.example .env

# Run dev server
poetry run uvicorn app.main:app --reload --port 8000
```

API will be at http://localhost:8000
Swagger docs at http://localhost:8000/docs

## Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
ng serve
```

Frontend will be at http://localhost:4200

## Running Tests

```bash
# Backend tests
cd backend
poetry run pytest

# With coverage
poetry run pytest --cov=app --cov-report=html
```

## Code Quality

```bash
# Linting
cd backend
poetry run ruff check app/
poetry run black --check app/
poetry run mypy app/

# Auto-fix
poetry run ruff check --fix app/
poetry run black app/
```

## Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

Hooks run automatically on `git commit`.

## Environment Variables

See `backend/.env.example` for all available settings.

Key settings:
- `ENVIRONMENT`: `development` | `production`
- `DEBUG`: Enable debug mode and docs
- `REDIS_URL`: Redis connection (optional, falls back to memory cache)
- `RATE_LIMIT_PER_MINUTE`: Per-IP rate limit for downloads
