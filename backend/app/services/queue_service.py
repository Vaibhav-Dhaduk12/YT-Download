import asyncio
from collections import deque
from typing import Any, Callable, Coroutine

import structlog

logger = structlog.get_logger()


class QueueService:
    def __init__(self, max_concurrent: int = 3) -> None:
        self._queue: deque = deque()
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._running = False

    async def enqueue(self, coro: Coroutine) -> None:
        self._queue.append(coro)
        if not self._running:
            asyncio.create_task(self._process())

    async def _process(self) -> None:
        self._running = True
        while self._queue:
            coro = self._queue.popleft()
            async with self._semaphore:
                try:
                    await coro
                except Exception as e:
                    logger.error("Queue task failed", error=str(e))
        self._running = False
