from aiohttp.client import ClientSession

_cached_raphson_logo = None


async def get_raphson_logo(session: ClientSession) -> bytes:
    global _cached_raphson_logo
    if not _cached_raphson_logo:
        async with session.get("/static/img/raphson.png") as response:
            _cached_raphson_logo = await response.content.read()
    return _cached_raphson_logo
