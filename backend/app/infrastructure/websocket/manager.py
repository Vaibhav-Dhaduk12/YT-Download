import json
from typing import Dict

import structlog
from fastapi import WebSocket

logger = structlog.get_logger()


class WebSocketManager:
    def __init__(self) -> None:
        self._connections: Dict[str, WebSocket] = {}

    async def connect(self, job_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections[job_id] = websocket
        logger.info("WebSocket connected", job_id=job_id)

    def disconnect(self, job_id: str) -> None:
        self._connections.pop(job_id, None)
        logger.info("WebSocket disconnected", job_id=job_id)

    async def send_progress(self, job_id: str, progress: float, status: str) -> None:
        websocket = self._connections.get(job_id)
        if websocket:
            try:
                await websocket.send_text(
                    json.dumps({"job_id": job_id, "progress": progress, "status": status})
                )
            except Exception as e:
                logger.warning("WebSocket send failed", job_id=job_id, error=str(e))
                self.disconnect(job_id)

    async def send_message(self, job_id: str, message: dict) -> None:
        websocket = self._connections.get(job_id)
        if websocket:
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.warning("WebSocket send failed", job_id=job_id, error=str(e))
                self.disconnect(job_id)


ws_manager = WebSocketManager()
