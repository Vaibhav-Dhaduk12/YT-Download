import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.exceptions.handlers import (
    rate_limit_handler,
    generic_exception_handler,
)
from app.api.v1.api import api_router
from app.config import get_settings
from app.core.rate_limiter import limiter
from app.infrastructure.tools.health_check import check_tools

logger = structlog.get_logger()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    os.makedirs(settings.temp_dir, exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    await check_tools()
    logger.info("Application started", environment=settings.environment)
    yield
    # Shutdown
    logger.info("Application shutting down")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="YouTube & Instagram video downloader API",
        docs_url="/docs" if settings.debug or settings.environment != "production" else None,
        redoc_url="/redoc" if settings.debug or settings.environment != "production" else None,
        lifespan=lifespan,
    )

    # Rate limiter
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, generic_exception_handler)  # type: ignore[arg-type]

    # Middlewares
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(SlowAPIMiddleware)

    # Routers
    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()
