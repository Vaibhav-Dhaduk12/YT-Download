import asyncio
import os
import re
import shutil
from typing import Any, Callable, Optional

import structlog
import yt_dlp

from app.api.exceptions.custom import DownloadError
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
            # Avoid inheriting user/global yt-dlp config (e.g. forced -f) that can break metadata.
            "ignoreconfig": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                return ydl.extract_info(url, download=False) or {}
            except yt_dlp.utils.DownloadError as exc:
                # Some videos can fail during format selection even for metadata calls.
                if "Requested format is not available" not in str(exc):
                    raise

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False, process=False) or {}

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

        ffmpeg_available = self._has_ffmpeg()
        candidates = self._build_format_candidates(format_id, quality, audio_only, ffmpeg_available)
        if not ffmpeg_available:
            logger.warning("ffmpeg not found, using non-merge download formats", url=url)

        output_template = os.path.join(output_dir, "%(id)s.%(ext)s")

        last_error: Optional[Exception] = None
        for fmt in candidates:
            ydl_opts: dict = {
                "format": fmt,
                "outtmpl": output_template,
                "quiet": False,
                "no_warnings": True,
                "ignoreconfig": True,
                "no_color": True,
            }

            if audio_only and ffmpeg_available:
                ydl_opts["postprocessors"] = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }]

            if progress_hook:
                ydl_opts["progress_hooks"] = [progress_hook]

            try:
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
            except yt_dlp.utils.DownloadError as exc:
                last_error = exc
                if "Requested format is not available" in str(exc):
                    logger.warning("Requested format unavailable, retrying", format=fmt, url=url)
                    continue
                if "ffmpeg is not installed" in str(exc):
                    logger.warning("ffmpeg unavailable for selected format, retrying", format=fmt, url=url)
                    continue
                raise DownloadError(self._clean_error(str(exc))) from exc

        if last_error:
            raise DownloadError(self._clean_error(str(last_error))) from last_error
        raise DownloadError("Download failed: no valid format found")

    def _build_format_candidates(
        self,
        format_id: Optional[str],
        quality: str,
        audio_only: bool,
        ffmpeg_available: bool,
    ) -> list[str]:
        candidates: list[str] = []
        if audio_only:
            if ffmpeg_available:
                candidates = ["bestaudio/best", "best"]
            else:
                candidates = ["bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio", "best"]
        elif format_id:
            if ffmpeg_available:
                candidates = [format_id, "bestvideo+bestaudio/best", "best"]
            else:
                if "+" in format_id:
                    candidates = [format_id.split("+")[0], "best[ext=mp4]/best", "best"]
                else:
                    candidates = [format_id, "best[ext=mp4]/best", "best"]
        elif quality == "best":
            if ffmpeg_available:
                candidates = ["bestvideo+bestaudio/best", "best"]
            else:
                candidates = ["best[ext=mp4]/best"]
        elif quality == "worst":
            if ffmpeg_available:
                candidates = ["worstvideo+worstaudio/worst", "worst"]
            else:
                candidates = ["worst[ext=mp4]/worst"]
        else:
            if ffmpeg_available:
                candidates = [
                    f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]",
                    "bestvideo+bestaudio/best",
                    "best",
                ]
            else:
                candidates = [
                    f"best[height<={quality}][ext=mp4]/best[height<={quality}]/best[ext=mp4]/best",
                ]

        # Preserve order while de-duplicating.
        return list(dict.fromkeys(candidates))

    def _has_ffmpeg(self) -> bool:
        return shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None

    def _clean_error(self, message: str) -> str:
        # Strip ANSI escapes so frontend displays readable errors.
        return re.sub(r"\x1b\[[0-9;]*m", "", message)
