from pathlib import Path

from tests import T_client


async def test_static(http_client: T_client):
    async with http_client.get("/static/img/raphson.png") as response:
        assert await response.read() == Path("raphson_mp/static/img/raphson.png").read_bytes()
