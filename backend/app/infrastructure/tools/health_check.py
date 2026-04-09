import asyncio
import shutil
from typing import Dict

import structlog

logger = structlog.get_logger()


async def check_tools() -> None:
    status = await get_tool_status()
    for tool, available in status.items():
        if available:
            logger.info(f"{tool} is available")
        else:
            logger.warning(f"{tool} is NOT available - some features may not work")


async def get_tool_status() -> Dict[str, bool]:
    loop = asyncio.get_event_loop()
    ffmpeg_available = await loop.run_in_executor(None, lambda: shutil.which("ffmpeg") is not None)
    ffprobe_available = await loop.run_in_executor(
        None, lambda: shutil.which("ffprobe") is not None
    )

    try:
        import yt_dlp
        ytdlp_available = True
    except ImportError:
        ytdlp_available = False

    return {
        "ffmpeg": ffmpeg_available,
        "ffprobe": ffprobe_available,
        "yt_dlp": ytdlp_available,
    }
