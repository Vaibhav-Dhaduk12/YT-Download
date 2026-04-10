# Deployment Guide

## Docker Compose (Recommended)

```bash
# Clone and configure
git clone https://github.com/Vaibhav-Dhaduk12/YT-Download.git
cd YT-Download

# Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env and set:
#   ENVIRONMENT=production
#   SECRET_KEY=<strong-random-key>
#   DEBUG=false

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

**Services:**
- Backend: http://localhost:8000
- Frontend: http://localhost:4200
- Redis: localhost:6379

## Manual Deployment

### Backend

```bash
cd backend
poetry install --no-dev
gunicorn app.main:app -c gunicorn_conf.py
```

### Frontend

```bash
cd frontend
npm run build:prod
# Serve dist/ with nginx or any static file server
```

## Environment Variables (Production)

```env
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<strong-random-string>
REDIS_URL=redis://redis:6379
ALLOWED_ORIGINS=https://yourdomain.com
RATE_LIMIT_PER_MINUTE=5
LOG_LEVEL=WARNING
```

## Health Check

```bash
curl http://localhost:8000/api/v1/health
```

## Updating

```bash
git pull
docker-compose build
docker-compose up -d
```
