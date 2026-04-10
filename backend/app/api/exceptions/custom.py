class MediaDownloaderError(Exception):
    """Base exception for media downloader."""


class InvalidURLError(MediaDownloaderError):
    """Raised when a URL is invalid or unsupported."""


class PlatformNotSupportedError(MediaDownloaderError):
    """Raised when platform is not supported."""


class DownloadError(MediaDownloaderError):
    """Raised when a download fails."""


class MetadataFetchError(MediaDownloaderError):
    """Raised when metadata cannot be fetched."""


class FormatNotFoundError(MediaDownloaderError):
    """Raised when requested format is not available."""


class FileSizeLimitError(MediaDownloaderError):
    """Raised when file exceeds the size limit."""


class RateLimitError(MediaDownloaderError):
    """Raised when rate limit is exceeded."""
