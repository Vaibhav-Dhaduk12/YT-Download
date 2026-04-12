import asyncio
import glob
import os
import shutil
from typing import Dict, Optional

import structlog

from app.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


def _existing_path(path: str) -> Optional[str]:
    candidate = (path or "").strip()
    if not candidate:
        return None
    return os.path.abspath(candidate) if os.path.exists(candidate) else None


def _iter_windows_fallback_paths(tool_name: str) -> list[str]:
    exe_name = f"{tool_name}.exe"
    localappdata = os.environ.get("LOCALAPPDATA", "")
    program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
    chocolatey_install = os.environ.get("ChocolateyInstall", "")

    fallback_paths: list[str] = [
        os.path.join(localappdata, "Microsoft", "WinGet", "Links", exe_name),
        os.path.join(program_files, "ffmpeg", "bin", exe_name),
        os.path.join("C:\\ffmpeg", "bin", exe_name),
    ]
    if chocolatey_install:
        fallback_paths.append(os.path.join(chocolatey_install, "bin", exe_name))

    winget_packages_glob = os.path.join(
        localappdata,
        "Microsoft",
        "WinGet",
        "Packages",
        "Gyan.FFmpeg_*",
    )
    for package_root in glob.glob(winget_packages_glob):
        for root, _, files in os.walk(package_root):
            if exe_name in files:
                fallback_paths.append(os.path.join(root, exe_name))
    return fallback_paths


def resolve_tool_path(tool_name: str) -> Optional[str]:
    env_var = f"{tool_name.upper()}_PATH"
    from_env = _existing_path(os.environ.get(env_var, ""))
    if from_env:
        return from_env

    if tool_name == "ffmpeg":
        from_settings = _existing_path(settings.ffmpeg_path)
        if from_settings:
            return from_settings
    elif tool_name == "ffprobe":
        from_settings = _existing_path(settings.ffprobe_path)
        if from_settings:
            return from_settings

    resolved = shutil.which(tool_name)
    if resolved:
        return os.path.abspath(resolved)

    if os.name == "nt" and tool_name in {"ffmpeg", "ffprobe"}:
        for candidate in _iter_windows_fallback_paths(tool_name):
            existing = _existing_path(candidate)
            if existing:
                return existing

    return None


def is_tool_available(tool_name: str) -> bool:
    return resolve_tool_path(tool_name) is not None


async def check_tools() -> None:
    status = await get_tool_status()
    for tool, available in status.items():
        if available:
            logger.info(f"{tool} is available")
        else:
            logger.warning(f"{tool} is NOT available - some features may not work")


async def get_tool_status() -> Dict[str, bool]:
    loop = asyncio.get_event_loop()
    ffmpeg_available = await loop.run_in_executor(None, lambda: is_tool_available("ffmpeg"))
    ffprobe_available = await loop.run_in_executor(None, lambda: is_tool_available("ffprobe"))

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
