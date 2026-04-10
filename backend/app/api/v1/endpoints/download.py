import structlog
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.api.exceptions.custom import InvalidURLError, PlatformNotSupportedError
from app.core.rate_limiter import limiter
from app.schemas.download import DownloadRequest, DownloadResponse
from app.services.download_service import DownloadService

router = APIRouter()
logger = structlog.get_logger()
download_service = DownloadService()


@router.post("", response_model=DownloadResponse)
@limiter.limit("10/minute")
async def start_download(
    request: Request,
    payload: DownloadRequest,
    background_tasks: BackgroundTasks,
) -> DownloadResponse:
    try:
        job = await download_service.create_job(payload)
        background_tasks.add_task(download_service.process_job, job.job_id)
        return DownloadResponse(
            job_id=job.job_id,
            status="queued",
            message="Download job created successfully",
        )
    except InvalidURLError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PlatformNotSupportedError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error("Download creation failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create download job")


@router.get("/{job_id}/status")
async def get_download_status(job_id: str) -> dict:
    status = await download_service.get_job_status(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    return status


@router.get("/{job_id}/stream")
async def stream_download(job_id: str) -> StreamingResponse:
    try:
        stream_response = await download_service.stream_file(job_id)
        return stream_response
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found or download not complete")
    except Exception as e:
        logger.error("Streaming failed", job_id=job_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to stream file")
