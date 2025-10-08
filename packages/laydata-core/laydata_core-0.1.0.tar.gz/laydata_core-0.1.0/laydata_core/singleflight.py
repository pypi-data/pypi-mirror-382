import asyncio
from contextlib import asynccontextmanager
from typing import Dict


class SingleFlight:
    """
    A simple per-process async singleflight lock registry.

    Usage:
        sf = get_singleflight()
        async with sf.lock(key):
            # Only one coroutine with the same key can enter here at a time
            ...
    """

    def __init__(self) -> None:
        self._locks: Dict[str, asyncio.Lock] = {}
        self._global_lock = asyncio.Lock()

    async def _get_lock(self, key: str) -> asyncio.Lock:
        # Double-checked creation under a global lock to avoid races when creating per-key locks
        lock = self._locks.get(key)
        if lock is not None:
            return lock
        async with self._global_lock:
            lock = self._locks.get(key)
            if lock is None:
                lock = asyncio.Lock()
                self._locks[key] = lock
            return lock

    @asynccontextmanager
    async def lock(self, key: str, timeout: float | None = None):
        l = await self._get_lock(key)
        acquired = False
        try:
            if timeout is None:
                await l.acquire()
                acquired = True
            else:
                await asyncio.wait_for(l.acquire(), timeout=timeout)
                acquired = True
            yield
        finally:
            if acquired:
                l.release()


_singleton: SingleFlight | None = None


def get_singleflight() -> SingleFlight:
    global _singleton
    if _singleton is None:
        _singleton = SingleFlight()
    return _singleton