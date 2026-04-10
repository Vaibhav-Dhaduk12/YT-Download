from app.config import Settings, get_settings
from fastapi import Depends
from functools import lru_cache


def get_app_settings(settings: Settings = Depends(get_settings)) -> Settings:
    return settings
