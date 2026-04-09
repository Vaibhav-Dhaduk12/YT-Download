import structlog
from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.exceptions.custom import InvalidURLError, PlatformNotSupportedError
from app.schemas.metadata import MetadataRequest, MetadataResponse
from app.services.metadata_service import MetadataService

router = APIRouter()
logger = structlog.get_logger()
limiter = Limiter(key_func=get_remote_address)
metadata_service = MetadataService()


@router.post("", response_model=MetadataResponse)
@limiter.limit("20/minute")
async def get_metadata(
    request: Request,
    payload: MetadataRequest,
) -> MetadataResponse:
    try:
        return await metadata_service.fetch_metadata(payload.url)
    except InvalidURLError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PlatformNotSupportedError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error("Metadata fetch failed", url=payload.url, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch metadata")
