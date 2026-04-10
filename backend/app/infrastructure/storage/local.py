import os
from pathlib import Path
from typing import Optional

import aiofiles
import structlog

from app.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


class LocalStorage:
    def __init__(self, base_dir: Optional[str] = None) -> None:
        self.base_dir = Path(base_dir or settings.temp_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def get_path(self, filename: str) -> Path:
        return self.base_dir / filename

    async def write(self, filename: str, data: bytes) -> Path:
        path = self.get_path(filename)
        async with aiofiles.open(path, "wb") as f:
            await f.write(data)
        return path

    async def read(self, filename: str) -> bytes:
        path = self.get_path(filename)
        async with aiofiles.open(path, "rb") as f:
            return await f.read()

    def delete(self, filename: str) -> bool:
        path = self.get_path(filename)
        try:
            path.unlink(missing_ok=True)
            return True
        except OSError as e:
            logger.error("Failed to delete file", path=str(path), error=str(e))
            return False

    def exists(self, filename: str) -> bool:
        return self.get_path(filename).exists()

    def list_files(self) -> list[str]:
        return [f.name for f in self.base_dir.iterdir() if f.is_file()]
