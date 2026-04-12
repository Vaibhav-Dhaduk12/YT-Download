import asyncio
import os
import re
import shutil
import subprocess
from typing import Any, Callable, Optional

import structlog
import yt_dlp

from app.api.exceptions.custom import DownloadError
from app.config import get_settings
from app.core.base import PlatformAdapter
from app.infrastructure.tools.health_check import resolve_tool_path
from app.schemas.metadata import MetadataResponse

logger = structlog.get_logger()
settings = get_settings()


class InstagramAdapter(PlatformAdapter):
    """Instagram platform adapter using yt-dlp with error recovery."""

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
            duration=self._normalize_duration(info.get("duration")),
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
        output_suffix: Optional[str] = None,
    ) -> dict:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self._do_download,
            url,
            format_id,
            audio_only,
            progress_hook,
            output_suffix,
        )
        return result

    def _fetch_info(self, url: str) -> dict:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "ignoreconfig": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False) or {}

    def _do_download(
        self,
        url: str,
        format_id: Optional[str],
        audio_only: bool,
        progress_hook: Optional[Callable[[dict], None]],
        output_suffix: Optional[str],
    ) -> dict:
        output_dir = os.path.abspath(settings.temp_dir)
        os.makedirs(output_dir, exist_ok=True)
        
        template_name = "%(id)s.%(ext)s"
        if output_suffix:
            template_name = f"%(id)s-{output_suffix}.%(ext)s"
        output_template = os.path.join(output_dir, template_name)

        # Build format candidates
        candidates = [format_id or "best", "best[ext=mp4]/best"]

        last_error: Optional[Exception] = None
        for attempt, fmt in enumerate(candidates):
            ydl_opts: dict = {
                "format": fmt,
                "outtmpl": output_template,
                "quiet": False,
                "no_warnings": True,
                "ignoreconfig": True,
                "overwrites": True,
            }

            if progress_hook:
                ydl_opts["progress_hooks"] = [progress_hook]

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True) or {}
                    filename = ydl.prepare_filename(info)

                # Validate output file
                is_valid, error_msg = self._validate_output_file(filename)
                if not is_valid:
                    logger.warning("Instagram output validation failed", 
                                 format=fmt, attempt=attempt, error=error_msg)
                    self._cleanup_partial_file(filename)
                    last_error = DownloadError(error_msg)
                    continue

                return {
                    "filepath": filename,
                    "filename": os.path.basename(filename),
                    "title": info.get("title") or info.get("description", "instagram_video"),
                    "ext": info.get("ext", "mp4"),
                }

            except yt_dlp.utils.DownloadError as exc:
                exc_str = str(exc)
                last_error = exc
                logger.warning("Instagram download attempt failed", attempt=attempt, 
                             format=fmt, error=exc_str[:100])
                
                if "Requested format is not available" in exc_str:
                    logger.info("Format unavailable, trying next candidate")
                    continue
                else:
                    # For other errors, try next candidate
                    continue

            except Exception as exc:
                exc_str = str(exc)
                last_error = exc
                logger.warning("Unexpected Instagram download error", 
                             attempt=attempt, error=exc_str[:100])
                
                # Clean up any partial files
                try:
                    for f in os.listdir(output_dir):
                        if ".part" in f:
                            self._cleanup_partial_file(os.path.join(output_dir, f))
                except Exception:
                    pass
                
                if attempt < len(candidates) - 1:
                    continue
                else:
                    raise DownloadError(self._clean_error(exc_str)) from exc

        if last_error:
            raise DownloadError(self._clean_error(str(last_error))) from last_error
        raise DownloadError("Instagram download failed: no valid format found")

    def _validate_output_file(self, filepath: str, min_size_kb: int = 100) -> tuple[bool, str]:
        """Validate that downloaded file is valid."""
        if not os.path.exists(filepath):
            return False, "Output file not created"
        
        try:
            file_size = os.path.getsize(filepath)
            min_bytes = min_size_kb * 1024
            
            if file_size < min_bytes:
                return False, f"File incomplete ({file_size} bytes < {min_bytes})"
            
            # Try ffprobe if available
            ffprobe_path = resolve_tool_path("ffprobe")
            if ffprobe_path:
                try:
                    result = subprocess.run(
                        [ffprobe_path, "-v", "error", "-show_entries", "stream=codec_type", 
                         "-of", "default=noprint_wrappers=1", filepath],
                        capture_output=True, text=True, timeout=5
                    )
                    if result.returncode != 0 or "codec_type=" not in result.stdout:
                        return False, "Container validation failed"
                except subprocess.TimeoutExpired:
                    pass  # Don't fail on timeout
                except Exception:
                    pass  # Don't fail on validation errors
            
            return True, ""
        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def _cleanup_partial_file(self, filepath: str) -> None:
        """Safely delete partial file."""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.debug("Partial file cleaned up", filepath=filepath)
        except Exception as e:
            logger.warning("Failed to cleanup partial file", error=str(e))

    def _normalize_duration(self, duration: Any) -> Optional[int]:
        if duration is None:
            return None
        try:
            return int(round(float(duration)))
        except (TypeError, ValueError):
            return None
