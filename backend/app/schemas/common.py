from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DownloadHistoryItem(BaseModel):
    job_id: str
    url: str
    title: str
    platform: str
    format: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    file_size: Optional[int] = None
    error: Optional[str] = None
