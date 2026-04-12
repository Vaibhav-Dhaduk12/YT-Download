# 🎬 YT-Download - YouTube & Instagram Video Downloader

A full-stack media downloader built with **FastAPI** (Python) and **Angular 17**.

> ⚠️ **Legal Notice**: Downloading copyrighted content may violate platform Terms of Service. This project is for **educational purposes only**. Always respect content creators' rights.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)
- FFmpeg + FFprobe (must be installed and available on PATH for high-quality video+audio merges)

#### FFmpeg setup (Windows)
```bash
winget install Gyan.FFmpeg
ffmpeg -version
ffprobe -version
```

### Option 1: Docker Compose (Recommended)
```bash
git clone https://github.com/Vaibhav-Dhaduk12/YT-Download.git
cd YT-Download
cp backend/.env.example backend/.env
docker-compose up -d
```
- Backend: http://localhost:8000
- Frontend: http://localhost:4200
- API Docs: http://localhost:8000/docs

### Option 2: Local Development
```bash
# Backend
cd backend
pip install poetry
poetry install
cp .env.example .env
poetry run uvicorn app.main:app --reload --port 8000

# Frontend (in another terminal)
cd frontend
npm install
ng serve
```

## 📁 Project Structure
```
YT-Download/
├── backend/          # FastAPI Python backend
├── frontend/         # Angular 17 frontend
├── docs/             # Documentation
└── scripts/          # Automation scripts
```

## 🔧 Features
- ✅ YouTube video/audio download via yt-dlp
- ✅ Instagram video download
- ✅ Multiple quality/format selection
- ✅ Real-time download progress via WebSocket
- ✅ Redis caching for metadata
- ✅ Rate limiting
- ✅ Docker support

## 📖 Documentation
- [API Reference](docs/API.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Development Setup](docs/DEVELOPMENT.md)
- [Contributing](docs/CONTRIBUTING.md)

## 📄 License
MIT License - Educational use only.
