import asyncio
import os
import shutil
from pathlib import Path
from typing import AsyncGenerator

import aiofiles
import structlog

logger = structlog.get_logger()


async def read_file_chunks(
    filepath: str,
    chunk_size: int = 65536,
) -> AsyncGenerator[bytes, None]:
    async with aiofiles.open(filepath, "rb") as f:
        while True:
            chunk = await f.read(chunk_size)
            if not chunk:
                break
            yield chunk


def get_file_size(filepath: str) -> int:
    return os.path.getsize(filepath) if os.path.exists(filepath) else 0


def safe_delete(filepath: str) -> bool:
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info("File deleted", filepath=filepath)
            return True
    except OSError as e:
        logger.error("Failed to delete file", filepath=filepath, error=str(e))
    return False


def cleanup_old_files(directory: str, max_age_seconds: int = 3600) -> int:
    import time

    deleted = 0
    try:
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                age = time.time() - os.path.getmtime(filepath)
                if age > max_age_seconds:
                    if safe_delete(filepath):
                        deleted += 1
    except OSError as e:
        logger.error("Cleanup failed", directory=directory, error=str(e))
    return deleted


def sanitize_filename(filename: str) -> str:
    invalid_chars = r'<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, "_")
    return filename.strip(". ")[:255]
