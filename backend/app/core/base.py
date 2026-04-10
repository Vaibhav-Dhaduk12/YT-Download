from abc import ABC, abstractmethod
from typing import Any, Callable, Optional

from app.schemas.metadata import MetadataResponse


class PlatformAdapter(ABC):
    """Abstract base class for platform-specific download adapters."""

    @abstractmethod
    async def get_metadata(self, url: str) -> MetadataResponse:
        """Fetch video metadata without downloading."""

    @abstractmethod
    async def download(
        self,
        url: str,
        format_id: Optional[str] = None,
        quality: str = "best",
        audio_only: bool = False,
        progress_hook: Optional[Callable[[dict], None]] = None,
        output_suffix: Optional[str] = None,
    ) -> dict:
        """
        Download video/audio.

        Returns dict with keys: filepath, filename, title, ext
        """

    @abstractmethod
    def supports(self, url: str) -> bool:
        """Return True if this adapter can handle the given URL."""
