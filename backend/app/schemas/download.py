from typing import Optional

from pydantic import BaseModel, field_validator


class DownloadRequest(BaseModel):
    url: str
    format_id: Optional[str] = None
    quality: Optional[str] = "best"
    audio_only: bool = False
    subtitles: bool = False

    @field_validator("quality")
    @classmethod
    def validate_quality(cls, value: Optional[str]) -> str:
        if value is None:
            return "best"

        normalized = value.strip().lower()
        if normalized in {"best", "worst"}:
            return normalized

        if normalized.endswith("p"):
            normalized = normalized[:-1]

        if not normalized.isdigit():
            raise ValueError("quality must be 'best', 'worst', or a numeric height like 480/720/1080")

        height = int(normalized)
        if height < 144 or height > 4320:
            raise ValueError("quality height must be between 144 and 4320")

        return str(height)


class DownloadResponse(BaseModel):
    job_id: str
    status: str
    message: str


class DownloadJob(BaseModel):
    job_id: str
    url: str
    format_id: Optional[str] = None
    quality: str = "best"
    audio_only: bool = False
    subtitles: bool = False
    status: str = "queued"
    progress: float = 0.0
    filename: Optional[str] = None
    file_path: Optional[str] = None
    error: Optional[str] = None
    title: Optional[str] = None
    platform: Optional[str] = None
