from app.core.base import PlatformAdapter
from app.core.instagram import InstagramAdapter
from app.core.youtube import YouTubeAdapter

_adapters: dict[str, PlatformAdapter] = {
    "youtube": YouTubeAdapter(),
    "instagram": InstagramAdapter(),
}


def get_platform_adapter(platform: str) -> PlatformAdapter:
    adapter = _adapters.get(platform.lower())
    if not adapter:
        raise ValueError(f"No adapter found for platform: {platform}")
    return adapter
