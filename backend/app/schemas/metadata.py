from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class MetadataRequest(BaseModel):
    url: str


class MetadataResponse(BaseModel):
    url: str
    platform: str
    video_id: str
    title: str
    description: Optional[str] = None
    duration: Optional[int] = None
    thumbnail: Optional[str] = None
    uploader: Optional[str] = None
    upload_date: Optional[str] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    formats: List[dict] = []
    is_live: bool = False
