import pytest

from app.utils.url_parser import (
    extract_instagram_id,
    extract_youtube_id,
    get_platform_from_url,
    normalize_url,
)


def test_extract_youtube_id_watch():
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert extract_youtube_id(url) == "dQw4w9WgXcQ"


def test_extract_youtube_id_short():
    url = "https://youtu.be/dQw4w9WgXcQ"
    assert extract_youtube_id(url) == "dQw4w9WgXcQ"


def test_extract_youtube_id_shorts():
    url = "https://www.youtube.com/shorts/dQw4w9WgXcQ"
    assert extract_youtube_id(url) == "dQw4w9WgXcQ"


def test_extract_instagram_id():
    url = "https://www.instagram.com/p/ABC123def/"
    assert extract_instagram_id(url) == "ABC123def"


def test_extract_instagram_reel_id():
    url = "https://www.instagram.com/reel/ABC123def/"
    assert extract_instagram_id(url) == "ABC123def"


def test_normalize_url_adds_https():
    assert normalize_url("youtube.com/watch?v=test") == "https://youtube.com/watch?v=test"


def test_normalize_url_strips_whitespace():
    assert normalize_url("  https://youtube.com/watch?v=test  ") == "https://youtube.com/watch?v=test"


def test_get_platform_youtube():
    assert get_platform_from_url("https://youtube.com/watch?v=test") == "youtube"


def test_get_platform_youtu_be():
    assert get_platform_from_url("https://youtu.be/test") == "youtube"


def test_get_platform_instagram():
    assert get_platform_from_url("https://instagram.com/p/test") == "instagram"


def test_get_platform_unknown():
    assert get_platform_from_url("https://tiktok.com/video/test") is None
