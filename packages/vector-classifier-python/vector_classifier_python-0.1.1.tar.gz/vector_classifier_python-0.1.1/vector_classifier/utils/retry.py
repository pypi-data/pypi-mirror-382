from __future__ import annotations
import asyncio
import random
from typing import Awaitable, Callable, TypeVar

T = TypeVar("T")

async def with_retry(fn: Callable[[], Awaitable[T]], *, retries: int = 3, min_delay_ms: int = 250, max_delay_ms: int = 4000) -> T:
    attempt = 0
    while True:
        try:
            return await fn()
        except Exception:  # noqa: BLE001
            attempt += 1
            if attempt > retries:
                raise
            jitter = random.random() * min_delay_ms
            delay = min(max_delay_ms, min_delay_ms * (2 ** (attempt - 1))) + jitter
            await asyncio.sleep(delay / 1000.0)

