import json
from typing import Optional

import structlog

from app.api.exceptions.custom import MetadataFetchError
from app.core.factory import get_platform_adapter
from app.schemas.metadata import MetadataResponse
from app.services.validation_service import ValidationService

logger = structlog.get_logger()


class MetadataService:
    def __init__(self) -> None:
        self.validation = ValidationService()
        self._cache: dict = {}

    async def fetch_metadata(self, url: str) -> MetadataResponse:
        url = self.validation.validate_url(url)
        platform = self.validation.detect_platform(url)

        if url in self._cache:
            logger.debug("Returning cached metadata", url=url)
            return self._cache[url]

        adapter = get_platform_adapter(platform)
        try:
            metadata = await adapter.get_metadata(url)
        except Exception as exc:
            message = str(exc)
            lowered = message.lower()

            if "sign in to confirm" in lowered and "not a bot" in lowered:
                raise MetadataFetchError(
                    "YouTube is blocking metadata retrieval for this video from server IP "
                    "(anti-bot challenge). Please try another video, try again later, or use "
                    "a backend setup with YouTube cookies configured for yt-dlp."
                ) from exc

            raise MetadataFetchError("Unable to fetch metadata for this URL.") from exc

        self._cache[url] = metadata
        return metadata
