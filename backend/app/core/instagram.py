import asyncio
import os
import re
from typing import Any, Callable, Optional

import structlog
import yt_dlp

from app.config import get_settings
from app.core.base import PlatformAdapter
from app.schemas.metadata import MetadataResponse

logger = structlog.get_logger()
settings = get_settings()


class InstagramAdapter(PlatformAdapter):
    """Instagram platform adapter using yt-dlp."""

    def supports(self, url: str) -> bool:
        patterns = [
            r"instagram\.com/p/",
            r"instagram\.com/reel/",
            r"instagram\.com/tv/",
        ]
        return any(re.search(p, url, re.IGNORECASE) for p in patterns)

    async def get_metadata(self, url: str) -> MetadataResponse:
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, self._fetch_info, url)

        return MetadataResponse(
            url=url,
            platform="instagram",
            video_id=info.get("id", ""),
            title=info.get("title") or info.get("description", "Instagram Video"),
            description=info.get("description"),
            duration=info.get("duration"),
            thumbnail=info.get("thumbnail"),
            uploader=info.get("uploader") or info.get("channel"),
            upload_date=info.get("upload_date"),
            view_count=info.get("view_count"),
            like_count=info.get("like_count"),
            formats=[
                {
                    "format_id": fmt.get("format_id"),
                    "ext": fmt.get("ext"),
                    "resolution": fmt.get("resolution"),
                    "filesize": fmt.get("filesize"),
                }
                for fmt in info.get("formats", [])
                if fmt.get("vcodec") != "none"
            ],
        )

    async def download(
        self,
        url: str,
        format_id: Optional[str] = None,
        quality: str = "best",
        audio_only: bool = False,
        progress_hook: Optional[Callable[[dict], None]] = None,
    ) -> dict:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self._do_download,
            url,
            format_id,
            audio_only,
            progress_hook,
        )
        return result

    def _fetch_info(self, url: str) -> dict:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False) or {}

    def _do_download(
        self,
        url: str,
        format_id: Optional[str],
        audio_only: bool,
        progress_hook: Optional[Callable[[dict], None]],
    ) -> dict:
        output_dir = os.path.abspath(settings.temp_dir)
        os.makedirs(output_dir, exist_ok=True)
        output_template = os.path.join(output_dir, "%(id)s.%(ext)s")

        ydl_opts: dict = {
            "format": format_id or "best",
            "outtmpl": output_template,
            "quiet": False,
            "no_warnings": True,
        }

        if progress_hook:
            ydl_opts["progress_hooks"] = [progress_hook]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True) or {}
            filename = ydl.prepare_filename(info)

        return {
            "filepath": filename,
            "filename": os.path.basename(filename),
            "title": info.get("title") or info.get("description", "instagram_video"),
            "ext": info.get("ext", "mp4"),
        }
