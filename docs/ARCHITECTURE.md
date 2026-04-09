# Architecture

## Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────┐
│  Angular 17     │────▶│  FastAPI Backend  │────▶│  yt-dlp     │
│  Frontend       │◀────│  (Python 3.11)    │     │  + FFmpeg   │
└─────────────────┘     └──────────────────┘     └─────────────┘
                                │
                                ▼
                         ┌─────────────┐
                         │    Redis    │
                         │   Cache     │
                         └─────────────┘
```

## Backend Structure

```
backend/app/
├── api/
│   ├── v1/
│   │   ├── endpoints/     # Route handlers
│   │   └── api.py         # Router aggregation
│   └── exceptions/        # Custom exceptions & handlers
├── core/                  # Platform adapters
│   ├── base.py            # Abstract PlatformAdapter
│   ├── youtube.py         # YouTube adapter
│   ├── instagram.py       # Instagram adapter
│   └── factory.py         # Adapter factory
├── services/              # Business logic
│   ├── metadata_service.py
│   ├── download_service.py
│   ├── validation_service.py
│   └── queue_service.py
├── schemas/               # Pydantic models
├── infrastructure/        # External integrations
│   ├── cache/             # Redis / in-memory cache
│   ├── storage/           # Local file storage
│   └── websocket/         # WebSocket manager
└── utils/                 # Helpers

```

## Key Design Decisions

### Platform Adapter Pattern
Each platform (YouTube, Instagram) implements the `PlatformAdapter` ABC. The factory returns the correct adapter based on URL detection. This makes it easy to add new platforms.

### Background Tasks
Downloads run as FastAPI `BackgroundTasks`, allowing the API to immediately return a job ID while processing happens asynchronously. Progress is tracked in-memory.

### Caching
Metadata is cached to avoid redundant yt-dlp calls. In development, an in-memory dict is used. In production, Redis provides distributed caching.

### Rate Limiting
`slowapi` provides per-IP rate limiting at the route level. Metadata: 20/min, Downloads: 10/min.
