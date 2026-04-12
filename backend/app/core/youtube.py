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
from app.infrastructure.tools.health_check import is_tool_available, resolve_tool_path
from app.schemas.format import FormatInfo
from app.schemas.metadata import MetadataResponse

logger = structlog.get_logger()
settings = get_settings()


class YouTubeAdapter(PlatformAdapter):
    """YouTube platform adapter using yt-dlp with robust error handling."""

    FFMPEG_REQUIRED_MSG = (
        "Selected format requires FFmpeg + FFprobe to merge video and audio. "
        "Install FFmpeg and ensure both `ffmpeg` and `ffprobe` are available on PATH, "
        "then retry. Windows: `winget install Gyan.FFmpeg`."
    )

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
            duration=self._normalize_duration(info.get("duration")),
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
        output_suffix: Optional[str] = None,
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
            output_suffix,
        )
        return result

    def _fetch_info(self, url: str) -> dict:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "ignoreconfig": True,
        }
        cookiefile = self._cookiefile_path()
        if cookiefile:
            ydl_opts["cookiefile"] = cookiefile
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                return ydl.extract_info(url, download=False) or {}
            except yt_dlp.utils.DownloadError as exc:
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
        output_suffix: Optional[str],
    ) -> dict:
        output_dir = os.path.abspath(settings.temp_dir)
        os.makedirs(output_dir, exist_ok=True)

        ffmpeg_path = resolve_tool_path("ffmpeg")
        ffmpeg_available = ffmpeg_path is not None and resolve_tool_path("ffprobe") is not None
        candidates = self._build_format_candidates(format_id, quality, audio_only, ffmpeg_available)
        if not ffmpeg_available:
            logger.warning("ffmpeg not found, using non-merge download formats", url=url)
            if format_id and not audio_only:
                raise DownloadError(self.FFMPEG_REQUIRED_MSG)

        template_name = "%(id)s.%(ext)s"
        if output_suffix:
            template_name = f"%(id)s-{output_suffix}.%(ext)s"
        output_template = os.path.join(output_dir, template_name)

        last_error: Optional[Exception] = None
        for attempt, fmt in enumerate(candidates):
            # Determine whether this format string triggers a mux/merge operation.
            # All merge format strings generated by _build_format_candidates contain
            # a literal "+" operator (e.g. "137+bestaudio/best") – plain format IDs
            # and quality filter strings never include "+", so this check is reliable.
            is_merge_format = ffmpeg_available and not audio_only and "+" in fmt

            ydl_opts: dict = {
                "format": fmt,
                "outtmpl": output_template,
                "quiet": False,
                "no_warnings": True,
                "ignoreconfig": True,
                "no_color": True,
                "overwrites": True,
            }
            if ffmpeg_path:
                ydl_opts["ffmpeg_location"] = os.path.dirname(ffmpeg_path)
            cookiefile = self._cookiefile_path()
            if cookiefile:
                ydl_opts["cookiefile"] = cookiefile

            if is_merge_format:
                # Ensure yt-dlp muxes into a universally playable container.
                ydl_opts["merge_output_format"] = "mp4"
                ydl_opts["prefer_ffmpeg"] = True

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

                    if is_merge_format:
                        # yt-dlp writes the merged output with the merge_output_format
                        # extension; replace whatever prepare_filename returned.
                        base, _ = os.path.splitext(filename)
                        filename = f"{base}.mp4"
                    elif audio_only and ffmpeg_available:
                        base, _ = os.path.splitext(filename)
                        filename = f"{base}.mp3"

                # Validate the output before returning
                is_valid, error_msg = self._validate_output_file(
                    filename,
                    require_video_stream=not audio_only,
                    require_audio_stream=True,
                )
                if not is_valid:
                    logger.warning("Output validation failed, retrying", 
                                 format=fmt, attempt=attempt, error=error_msg, url=url)
                    self._cleanup_partial_file(filename)
                    last_error = DownloadError(error_msg)
                    continue

                if is_merge_format:
                    output_ext = "mp4"
                elif audio_only and ffmpeg_available:
                    output_ext = "mp3"
                else:
                    output_ext = info.get("ext", "mp4")

                return {
                    "filepath": filename,
                    "filename": os.path.basename(filename),
                    "title": info.get("title", "download"),
                    "ext": output_ext,
                }

            except yt_dlp.utils.DownloadError as exc:
                exc_str = str(exc)
                last_error = exc
                
                logger.warning("Download attempt failed", attempt=attempt, format=fmt, 
                             error=exc_str[:100], url=url)
                
                # Handle specific error types
                if "Requested format is not available" in exc_str:
                    logger.info("Trying next format candidate", format=fmt)
                    # Attempt cleanup of any partial file
                    try:
                        partial = os.path.join(output_dir, f"{info.get('id', 'unknown')}.partial")
                        self._cleanup_partial_file(partial)
                    except Exception:
                        pass
                    continue
                    
                elif "ffmpeg is not installed" in exc_str or "ffmpeg" in exc_str.lower():
                    logger.info("ffmpeg unavailable for this format, trying next candidate")
                    continue
                    
                elif "postprocessor" in exc_str.lower() or "mux" in exc_str.lower() or "merge" in exc_str.lower():
                    logger.warning("Postprocessor/mux error encountered, trying next video candidate")
                    continue
                    
                else:
                    # For unexpected errors, raise immediately
                    raise DownloadError(self._clean_error(exc_str)) from exc

            except Exception as exc:
                # Catch any other exceptions (postprocessor, IO, etc.)
                exc_str = str(exc)
                logger.warning("Unexpected error during download", attempt=attempt, 
                             format=fmt, error=exc_str[:100])
                last_error = exc
                
                # Attempt cleanup of partial files
                try:
                    for file in os.listdir(output_dir):
                        if ".part" in file or ".info" in file:
                            self._cleanup_partial_file(os.path.join(output_dir, file))
                except Exception:
                    pass
                
                # If this looks like a postprocessor error, try next candidate
                if "postprocessor" in exc_str.lower() or "mux" in exc_str.lower():
                    continue
                
                # Otherwise keep trying other candidates
                if attempt < len(candidates) - 1:
                    continue
                else:
                    raise DownloadError(self._clean_error(exc_str)) from exc

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
                # Force merge of selected video format with best available audio so the
                # output is always playable (many YouTube format_ids are video-only).
                candidates = [
                    f"{format_id}+bestaudio[ext=m4a]/bestaudio/best",
                    "bestvideo+bestaudio[ext=m4a]/bestaudio/best",
                    "best",
                ]
            else:
                # No ffmpeg available – fall back to progressive formats that carry audio.
                candidates = [
                    "best[ext=mp4][acodec^=mp4a][vcodec!=none]",
                    "best[ext=mp4][acodec!=none][vcodec!=none]",
                ]
        elif quality == "best":
            if ffmpeg_available:
                candidates = ["bestvideo+bestaudio[ext=m4a]/bestaudio/best", "best"]
            else:
                candidates = [
                    "best[ext=mp4][acodec^=mp4a][vcodec!=none]",
                    "best[ext=mp4][acodec!=none][vcodec!=none]",
                ]
        elif quality == "worst":
            if ffmpeg_available:
                candidates = ["worstvideo+worstaudio[ext=m4a]/worstaudio/worst", "worst"]
            else:
                candidates = [
                    "worst[ext=mp4][acodec^=mp4a][vcodec!=none]",
                    "worst[ext=mp4][acodec!=none][vcodec!=none]",
                    "best[ext=mp4][acodec^=mp4a][vcodec!=none]",
                ]
        else:
            height = int(quality)
            if ffmpeg_available:
                candidates = [
                    f"bestvideo[height<={height}]+bestaudio[ext=m4a]/bestaudio/best[height<={height}]",
                    f"best[height<={height}][acodec!=none]/best[height<={height}]",
                    "best[acodec!=none]/best",
                    "best",
                ]
            else:
                candidates = [
                    f"best[height<={height}][ext=mp4][acodec^=mp4a][vcodec!=none]",
                    f"best[height<={height}][ext=mp4][acodec!=none][vcodec!=none]",
                    "best[ext=mp4][acodec^=mp4a][vcodec!=none]",
                    "best[ext=mp4][acodec!=none][vcodec!=none]",
                ]

        return list(dict.fromkeys(candidates))

    def _validate_output_file(
        self,
        filepath: str,
        min_size_kb: int = 100,
        require_video_stream: bool = False,
        require_audio_stream: bool = False,
    ) -> tuple[bool, str]:
        """
        Validate that downloaded file exists and has reasonable size and structure.
        Returns: (is_valid, error_message)
        """
        if not os.path.exists(filepath):
            return False, "Output file not created"
        
        try:
            file_size = os.path.getsize(filepath)
            min_bytes = min_size_kb * 1024
            
            if file_size < min_bytes:
                return False, f"File too small ({file_size} bytes, expected at least {min_bytes} bytes)"
            
            # Try ffprobe validation if available (checks container/codecs)
            ffprobe_path = resolve_tool_path("ffprobe")
            if ffprobe_path:
                try:
                    result = subprocess.run(
                        [ffprobe_path, "-v", "error", "-show_entries", "stream=codec_type", 
                         "-of", "default=noprint_wrappers=1", filepath],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    
                    if result.returncode != 0:
                        logger.warning("ffprobe check failed with non-zero return", 
                                     filepath=filepath, returncode=result.returncode)
                        return False, "Container validation failed"
                    
                    if "codec_type=" not in result.stdout:
                        return False, "No valid streams in output (possibly corrupted)"

                    stream_types = {
                        line.split("=", 1)[1].strip()
                        for line in result.stdout.splitlines()
                        if line.startswith("codec_type=") and "=" in line
                    }
                    if require_video_stream and "video" not in stream_types:
                        return False, "Output missing video stream"
                    if require_audio_stream and "audio" not in stream_types:
                        return False, "Output missing audio stream"
                    
                except subprocess.TimeoutExpired:
                    logger.warning("ffprobe validation timeout", filepath=filepath)
                    # Too slow but file might be OK, don't fail here
                except Exception as e:
                    logger.debug("ffprobe validation error (continuing anyway)", 
                               filepath=filepath, error=str(e))
            
            return True, ""
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def _cleanup_partial_file(self, filepath: str) -> None:
        """Safely delete a partial or failed download."""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.debug("Partial file cleaned up", filepath=filepath)
        except Exception as e:
            logger.warning("Failed to cleanup partial file", filepath=filepath, error=str(e))

    def _has_ffmpeg(self) -> bool:
        return is_tool_available("ffmpeg") and is_tool_available("ffprobe")

    def _cookiefile_path(self) -> Optional[str]:
        cookiefile = (settings.ytdlp_cookiefile or "").strip()
        if cookiefile and os.path.exists(cookiefile):
            return cookiefile
        return None

    def _clean_error(self, message: str) -> str:
        return re.sub(r"\x1b\[[0-9;]*m", "", message)

    def _normalize_duration(self, duration: Any) -> Optional[int]:
        if duration is None:
            return None
        try:
            return int(round(float(duration)))
        except (TypeError, ValueError):
            return None
