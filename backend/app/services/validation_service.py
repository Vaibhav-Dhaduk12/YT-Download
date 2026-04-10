import re
from typing import Optional
from urllib.parse import urlparse

from app.api.exceptions.custom import InvalidURLError, PlatformNotSupportedError

SUPPORTED_PLATFORMS = {
    "youtube": [
        r"(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+",
        r"(?:https?://)?(?:www\.)?youtube\.com/shorts/[\w-]+",
        r"(?:https?://)?youtu\.be/[\w-]+",
        r"(?:https?://)?(?:www\.)?youtube\.com/playlist\?list=[\w-]+",
    ],
    "instagram": [
        r"(?:https?://)?(?:www\.)?instagram\.com/p/[\w-]+",
        r"(?:https?://)?(?:www\.)?instagram\.com/reel/[\w-]+",
        r"(?:https?://)?(?:www\.)?instagram\.com/tv/[\w-]+",
    ],
}


class ValidationService:
    def validate_url(self, url: str) -> str:
        url = url.strip()
        if not url:
            raise InvalidURLError("URL cannot be empty")

        try:
            parsed = urlparse(url)
            if not parsed.scheme:
                url = f"https://{url}"
                parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"):
                raise InvalidURLError(f"Invalid URL scheme: {parsed.scheme}")
            if not parsed.netloc:
                raise InvalidURLError("Invalid URL: missing domain")
        except Exception as e:
            if isinstance(e, InvalidURLError):
                raise
            raise InvalidURLError(f"Invalid URL: {e}")

        return url

    def detect_platform(self, url: str) -> str:
        for platform, patterns in SUPPORTED_PLATFORMS.items():
            for pattern in patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    return platform
        raise PlatformNotSupportedError(
            f"URL does not match any supported platform. "
            f"Supported: {', '.join(SUPPORTED_PLATFORMS.keys())}"
        )

    def is_supported(self, url: str) -> bool:
        try:
            self.detect_platform(url)
            return True
        except PlatformNotSupportedError:
            return False
