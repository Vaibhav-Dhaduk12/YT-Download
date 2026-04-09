import json
from typing import Optional

import structlog

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
        metadata = await adapter.get_metadata(url)

        self._cache[url] = metadata
        return metadata
