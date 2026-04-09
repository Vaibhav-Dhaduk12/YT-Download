import asyncio
import os
import re
from typing import Any, Callable, Optional

import structlog
import yt_dlp

from app.config import get_settings
from app.core.base import PlatformAdapter
from app.schemas.format import FormatInfo
from app.schemas.metadata import MetadataResponse

logger = structlog.get_logger()
settings = get_settings()


class YouTubeAdapter(PlatformAdapter):
    """YouTube platform adapter using yt-dlp."""

    def supports(self, url: str) -> bool:
        patterns = [
            r"youtube\.com/watch",
            r"youtube\.com/shorts",
            r"youtu\.be/",
            r"youtube\.com/playlist",
        ]
        return any(re.search(p, url, re.IGNORECASE) for p in patterns)

    async def get_metadata(self, url: str) -> MetadataResponse:
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, self._fetch_info, url)

        formats = []
        for fmt in info.get("formats", []):
            if fmt.get("vcodec") != "none" or fmt.get("acodec") != "none":
                formats.append({
                    "format_id": fmt.get("format_id"),
                    "ext": fmt.get("ext"),
                    "resolution": fmt.get("resolution") or (
                        f"{fmt.get('width')}x{fmt.get('height')}"
                        if fmt.get("width") and fmt.get("height")
                        else None
                    ),
                    "fps": fmt.get("fps"),
                    "vcodec": fmt.get("vcodec"),
                    "acodec": fmt.get("acodec"),
                    "filesize": fmt.get("filesize"),
                    "filesize_approx": fmt.get("filesize_approx"),
                    "tbr": fmt.get("tbr"),
                    "format_note": fmt.get("format_note"),
                })

        return MetadataResponse(
            url=url,
            platform="youtube",
            video_id=info.get("id", ""),
            title=info.get("title", "Unknown"),
            description=info.get("description"),
            duration=info.get("duration"),
            thumbnail=info.get("thumbnail"),
            uploader=info.get("uploader") or info.get("channel"),
            upload_date=info.get("upload_date"),
            view_count=info.get("view_count"),
            like_count=info.get("like_count"),
            formats=formats,
            is_live=info.get("is_live", False),
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
            quality,
            audio_only,
            progress_hook,
        )
        return result

    def _fetch_info(self, url: str) -> dict:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False) or {}

    def _do_download(
        self,
        url: str,
        format_id: Optional[str],
        quality: str,
        audio_only: bool,
        progress_hook: Optional[Callable[[dict], None]],
    ) -> dict:
        output_dir = os.path.abspath(settings.temp_dir)
        os.makedirs(output_dir, exist_ok=True)

        if audio_only:
            fmt = "bestaudio/best"
        elif format_id:
            fmt = format_id
        elif quality == "best":
            fmt = "bestvideo+bestaudio/best"
        elif quality == "worst":
            fmt = "worstvideo+worstaudio/worst"
        else:
            fmt = f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]"

        output_template = os.path.join(output_dir, "%(id)s.%(ext)s")

        ydl_opts: dict = {
            "format": fmt,
            "outtmpl": output_template,
            "quiet": False,
            "no_warnings": True,
        }

        if audio_only:
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]

        if progress_hook:
            ydl_opts["progress_hooks"] = [progress_hook]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True) or {}
            filename = ydl.prepare_filename(info)
            if audio_only:
                base, _ = os.path.splitext(filename)
                filename = f"{base}.mp3"

        return {
            "filepath": filename,
            "filename": os.path.basename(filename),
            "title": info.get("title", "download"),
            "ext": info.get("ext", "mp4"),
        }
