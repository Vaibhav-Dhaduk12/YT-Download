from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "MediaDownloader"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False
    secret_key: str = "change-me-in-production"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1

    # CORS
    allowed_origins: str = "http://localhost:4200,http://localhost:3000"

    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_ttl: int = 3600

    # Rate Limiting
    rate_limit_per_minute: int = 10
    rate_limit_per_hour: int = 100

    # Download
    temp_dir: str = "./temp"
    max_file_size_mb: int = 500
    download_timeout: int = 300
    ffmpeg_path: str = ""
    ffprobe_path: str = ""
    ytdlp_cookiefile: str = ""

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    @property
    def allowed_origins_list(self) -> List[str]:
        value = self.allowed_origins.strip()
        if value.startswith("[") and value.endswith("]"):
            # Accept JSON-style arrays for compatibility with existing env setups.
            import json

            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [str(origin).strip() for origin in parsed if str(origin).strip()]
        return [origin.strip() for origin in value.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
