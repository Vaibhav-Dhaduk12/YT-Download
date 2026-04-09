from fastapi import APIRouter

from app.api.v1.endpoints.download import router as download_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.history import router as history_router
from app.api.v1.endpoints.metadata import router as metadata_router

api_router = APIRouter()

api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(metadata_router, prefix="/metadata", tags=["metadata"])
api_router.include_router(download_router, prefix="/download", tags=["download"])
api_router.include_router(history_router, prefix="/history", tags=["history"])
