import platform
import sys

from fastapi import APIRouter
from pydantic import BaseModel

from app.config import get_settings
from app.infrastructure.tools.health_check import get_tool_status

router = APIRouter()
settings = get_settings()


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    python_version: str
    tools: dict


@router.get("", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    tool_status = await get_tool_status()
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        environment=settings.environment,
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        tools=tool_status,
    )
