import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, ParamSpec

import aiohttp

from raphson_mp.common.const import PACKAGE_VERSION

_LOGGER = logging.getLogger(__name__)

USER_AGENT = f"raphson-music-player/{PACKAGE_VERSION} (https://codeberg.org/raphson/music-server)"
WEBSCRAPING_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0"  # https://useragents.me
)

_cached_connector: aiohttp.TCPConnector | None = None


P = ParamSpec("P")


@asynccontextmanager
async def session(
    base_url: str | None = None, scraping: bool = False, **kwargs: Any
) -> AsyncIterator[aiohttp.ClientSession]:
    kwargs.setdefault("raise_for_status", True)
    kwargs.setdefault("timeout", aiohttp.ClientTimeout(total=10, connect=5, sock_connect=5))

    user_agent = WEBSCRAPING_USER_AGENT if scraping else USER_AGENT
    if "headers" in kwargs:
        kwargs["headers"].setdefault("User-Agent", user_agent)
    else:
        kwargs.setdefault("headers", {"User-Agent": user_agent})

    global _cached_connector
    if _cached_connector is not None:
        kwargs.setdefault("connector", _cached_connector)
        kwargs.setdefault("connector_owner", False)

    session = aiohttp.ClientSession(base_url, **kwargs)
    try:
        yield session
    finally:
        await session.close()


def enable_cached_connector() -> None:
    """Use a cached connector. You must call close() manually."""
    _LOGGER.debug("initializing connector")
    global _cached_connector
    assert _cached_connector is None or _cached_connector.closed
    _cached_connector = aiohttp.TCPConnector()


async def close():
    _LOGGER.debug("closing connector")
    global _cached_connector
    assert _cached_connector
    await _cached_connector.close()
    _cached_connector = None
