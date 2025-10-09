"""
Functions related to the cache (cache.db)
"""

import asyncio
import logging
import random
import time
from collections.abc import Awaitable
from dataclasses import dataclass
from typing import Any, Callable, ParamSpec, cast
from weakref import WeakValueDictionary
from raphson_mp.server import db

log = logging.getLogger(__name__)

HOUR = 60 * 60
DAY = 24 * HOUR
WEEK = 7 * DAY
MONTH = 30 * DAY
HALFYEAR = 6 * MONTH
YEAR = 12 * MONTH


async def store(key: str, data: bytes, duration: int) -> None:
    """
    Args:
        key: Cache key
        data: Data to cache
        duration: Suggested cache duration in seconds. Cache duration is varied by up to 25%, to
                  avoid high load when cache entries all expire at roughly the same time.
    """
    log.debug("storing in cache: %s", key)

    # Vary cache duration so cached data doesn't expire all at once
    duration += random.randint(-duration // 4, duration // 4)

    expire_time = int(time.time()) + duration

    def thread():
        with db.CACHE.connect() as conn:
            conn.execute(
                """
                INSERT INTO cache (key, data, expire_time, external)
                VALUES (?, ?, ?, false)
                """,
                (key, data, expire_time),
            )

    await asyncio.to_thread(thread)


async def retrieve(key: str) -> bytes | None:
    """
    Retrieve object from cache
    Args:
        key: Cache key
        partial: Return partial data in the specified range (start, length)
        return_expired: Whether to return the object from cache even when expired, but not cleaned
                        up yet. Should be set to False for short lived cache objects.
    """

    with db.CACHE.connect() as conn:
        row = cast(tuple[bytes] | None, conn.execute("SELECT data FROM cache WHERE key=?", (key,)).fetchone())

    if row is None:
        log.debug("not cached: %s", key)
        return None

    log.debug("retrieved from cache: %s", key)
    return row[0]


@dataclass
class CacheData:
    data: bytes
    duration: int


P = ParamSpec("P")
LOCKS: WeakValueDictionary[str, asyncio.Lock] = WeakValueDictionary()


async def retrieve_or_store(
    key: str, data_func: Callable[P, Awaitable[CacheData]], *args: P.args, **kwargs: P.kwargs
) -> bytes:
    async def retrieve_store():
        cache = await data_func(*args, **kwargs)
        await store(key, cache.data, cache.duration)
        return cache.data

    # Some clients make repeated requests to a cached resource, aborting the request just before
    # the resource has been written to the cache. Use shield() to prevent this.
    async def shielded():
        lock = LOCKS.get(key)
        if not lock:
            LOCKS[key] = lock = asyncio.Lock()
        async with lock:
            data = await retrieve(key)
            if data is not None:
                return data
            return await retrieve_store()

    return await asyncio.shield(shielded())


async def delete(key: str):
    def thread():
        with db.CACHE.connect() as conn:
            conn.execute("DELETE FROM cache WHERE key = ?", (key,))

    return await asyncio.to_thread(thread)


async def cleanup() -> None:
    """
    Remove some cache entries that are beyond their expire time.
    """

    def thread() -> list[str]:
        with db.CACHE.connect() as conn:
            to_delete: list[str] = []
            for key in MEMORY_CACHE:
                if MEMORY_CACHE[key].expire > time.time():
                    to_delete.append(key)
            for key in to_delete:
                del MEMORY_CACHE[key]

            return [
                cast(str, row[0])
                for row in conn.execute("SELECT key FROM cache WHERE expire_time < ? LIMIT 100", (int(time.time()),))
            ]

    keys = await asyncio.to_thread(thread)
    for key in keys:
        await delete(key)
    log.info("deleted %s entries from cache", len(keys))


@dataclass
class MemoryCacheEntry:
    data: Any
    expire: float


MEMORY_CACHE: dict[str, MemoryCacheEntry] = {}


def memory_store(key: str, data: Any, duration: float) -> None:
    MEMORY_CACHE[key] = MemoryCacheEntry(data, time.time() + duration)


def memory_get(key: str) -> Any | None:
    entry = MEMORY_CACHE.get(key)
    if entry is None:
        return None

    if entry.expire < time.time():
        del MEMORY_CACHE[key]
        return None

    return entry.data
