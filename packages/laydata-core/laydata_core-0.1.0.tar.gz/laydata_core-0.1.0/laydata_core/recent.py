import asyncio
import time
from typing import Any, Dict, Tuple


class RecentRegistry:
    """
    A tiny in-memory TTL cache for recently created resources.
    Used to bridge eventual consistency windows after create.
    """

    def __init__(self) -> None:
        self._data: Dict[str, Tuple[Any, float]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str):
        now = time.time()
        async with self._lock:
            entry = self._data.get(key)
            if not entry:
                return None
            value, expires = entry
            if expires < now:
                # Expired; drop
                self._data.pop(key, None)
                return None
            return value

    async def set(self, key: str, value: Any, ttl_sec: float):
        expires = time.time() + ttl_sec
        async with self._lock:
            self._data[key] = (value, expires)


_singleton: RecentRegistry | None = None


def get_recent_registry() -> RecentRegistry:
    global _singleton
    if _singleton is None:
        _singleton = RecentRegistry()
    return _singleton