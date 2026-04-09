import pytest

from app.api.exceptions.custom import InvalidURLError, PlatformNotSupportedError
from app.services.validation_service import ValidationService


@pytest.fixture
def service():
    return ValidationService()


def test_validate_valid_url(service):
    url = service.validate_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


def test_validate_url_adds_https(service):
    url = service.validate_url("youtube.com/watch?v=dQw4w9WgXcQ")
    assert url.startswith("https://")


def test_validate_empty_url(service):
    with pytest.raises(InvalidURLError):
        service.validate_url("")


def test_validate_invalid_scheme(service):
    with pytest.raises(InvalidURLError):
        service.validate_url("ftp://youtube.com/watch?v=test")


def test_detect_youtube(service):
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert service.detect_platform(url) == "youtube"


def test_detect_youtube_short(service):
    url = "https://youtu.be/dQw4w9WgXcQ"
    assert service.detect_platform(url) == "youtube"


def test_detect_instagram(service):
    url = "https://www.instagram.com/p/ABC123def/"
    assert service.detect_platform(url) == "instagram"


def test_detect_instagram_reel(service):
    url = "https://www.instagram.com/reel/ABC123def/"
    assert service.detect_platform(url) == "instagram"


def test_detect_unsupported(service):
    with pytest.raises(PlatformNotSupportedError):
        service.detect_platform("https://tiktok.com/video/12345")


def test_is_supported_true(service):
    assert service.is_supported("https://www.youtube.com/watch?v=dQw4w9WgXcQ") is True


def test_is_supported_false(service):
    assert service.is_supported("https://tiktok.com/video/12345") is False
