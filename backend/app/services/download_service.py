import uuid
from typing import Optional

import aiofiles
import structlog
from fastapi.responses import StreamingResponse

from app.core.factory import get_platform_adapter
from app.schemas.download import DownloadJob, DownloadRequest
from app.services.validation_service import ValidationService

logger = structlog.get_logger()


class DownloadService:
    def __init__(self) -> None:
        self.validation = ValidationService()
        self._jobs: dict[str, DownloadJob] = {}

    async def create_job(self, request: DownloadRequest) -> DownloadJob:
        url = self.validation.validate_url(request.url)
        platform = self.validation.detect_platform(url)

        job = DownloadJob(
            job_id=str(uuid.uuid4()),
            url=url,
            format_id=request.format_id,
            quality=request.quality or "best",
            audio_only=request.audio_only,
            subtitles=request.subtitles,
            platform=platform,
            status="queued",
        )
        self._jobs[job.job_id] = job
        logger.info("Download job created", job_id=job.job_id, platform=platform, url=url)
        return job

    async def process_job(self, job_id: str) -> None:
        job = self._jobs.get(job_id)
        if not job:
            logger.error("Job not found", job_id=job_id)
            return

        job.status = "processing"
        try:
            adapter = get_platform_adapter(job.platform or "youtube")

            def progress_hook(d: dict) -> None:
                if d.get("status") == "downloading":
                    total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
                    downloaded = d.get("downloaded_bytes", 0)
                    if total > 0:
                        job.progress = round((downloaded / total) * 100, 1)

            result = await adapter.download(
                url=job.url,
                format_id=job.format_id,
                quality=job.quality,
                audio_only=job.audio_only,
                progress_hook=progress_hook,
            )

            job.file_path = result.get("filepath")
            job.filename = result.get("filename")
            job.title = result.get("title")
            job.status = "completed"
            job.progress = 100.0
            logger.info("Download completed", job_id=job_id, filename=job.filename)
        except Exception as e:
            job.status = "failed"
            job.error = str(e)
            logger.error("Download failed", job_id=job_id, error=str(e))

    async def get_job_status(self, job_id: str) -> Optional[dict]:
        job = self._jobs.get(job_id)
        if not job:
            return None
        return job.model_dump()

    async def stream_file(self, job_id: str) -> StreamingResponse:
        job = self._jobs.get(job_id)
        if not job or job.status != "completed" or not job.file_path:
            raise FileNotFoundError(f"File not ready for job {job_id}")

        import os
        if not os.path.exists(job.file_path):
            raise FileNotFoundError(f"File not found: {job.file_path}")

        filename = job.filename or "download"

        async def file_generator():
            async with aiofiles.open(job.file_path, "rb") as f:
                while chunk := await f.read(65536):
                    yield chunk

        return StreamingResponse(
            file_generator(),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
