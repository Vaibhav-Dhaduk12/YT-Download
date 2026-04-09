from typing import Optional

from pydantic import BaseModel


class DownloadRequest(BaseModel):
    url: str
    format_id: Optional[str] = None
    quality: Optional[str] = "best"
    audio_only: bool = False
    subtitles: bool = False


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
