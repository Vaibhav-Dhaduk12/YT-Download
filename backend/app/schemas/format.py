from typing import Optional

from pydantic import BaseModel


class FormatInfo(BaseModel):
    format_id: str
    ext: str
    resolution: Optional[str] = None
    fps: Optional[float] = None
    vcodec: Optional[str] = None
    acodec: Optional[str] = None
    filesize: Optional[int] = None
    filesize_approx: Optional[int] = None
    tbr: Optional[float] = None
    vbr: Optional[float] = None
    abr: Optional[float] = None
    quality: Optional[float] = None
    format_note: Optional[str] = None
    language: Optional[str] = None
