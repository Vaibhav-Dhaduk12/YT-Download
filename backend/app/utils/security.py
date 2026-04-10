import os
import re
from pathlib import Path
from typing import Optional

import structlog

logger = structlog.get_logger()

DANGEROUS_PATH_CHARS = re.compile(r"[;&|`$><!\n\r\t]")


def sanitize_url(url: str) -> str:
    url = url.strip()
    if DANGEROUS_PATH_CHARS.search(url):
        raise ValueError("URL contains invalid characters")
    return url


def validate_file_path(filepath: str, base_dir: str) -> bool:
    try:
        resolved = Path(filepath).resolve()
        base = Path(base_dir).resolve()
        return resolved.is_relative_to(base)
    except (OSError, ValueError):
        return False


def sanitize_format_id(format_id: Optional[str]) -> Optional[str]:
    if format_id is None:
        return None
    if not re.match(r"^[\w\-\+]+$", format_id):
        raise ValueError(f"Invalid format ID: {format_id}")
    return format_id
