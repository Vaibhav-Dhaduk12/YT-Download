import re
from typing import Optional
from urllib.parse import parse_qs, urlparse


def extract_youtube_id(url: str) -> Optional[str]:
    patterns = [
        r"(?:v=|youtu\.be/|shorts/)([a-zA-Z0-9_-]{11})",
        r"(?:embed/)([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def extract_instagram_id(url: str) -> Optional[str]:
    match = re.search(r"instagram\.com/(?:p|reel|tv)/([\w-]+)", url)
    return match.group(1) if match else None


def normalize_url(url: str) -> str:
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    return url


def get_platform_from_url(url: str) -> Optional[str]:
    try:
        hostname = urlparse(url).hostname or ""
        hostname = hostname.lower()
    except Exception:
        return None
    if hostname in ("youtube.com", "www.youtube.com", "youtu.be", "m.youtube.com"):
        return "youtube"
    if hostname in ("instagram.com", "www.instagram.com"):
        return "instagram"
    return None
