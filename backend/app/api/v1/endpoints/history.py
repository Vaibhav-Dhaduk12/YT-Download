from fastapi import APIRouter
from typing import List

from app.schemas.common import DownloadHistoryItem

router = APIRouter()

_history: List[DownloadHistoryItem] = []


@router.get("", response_model=List[DownloadHistoryItem])
async def get_history() -> List[DownloadHistoryItem]:
    return list(reversed(_history))


@router.delete("")
async def clear_history() -> dict:
    _history.clear()
    return {"message": "History cleared"}
