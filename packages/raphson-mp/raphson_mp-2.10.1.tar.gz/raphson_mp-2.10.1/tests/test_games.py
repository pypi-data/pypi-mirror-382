from . import T_client


async def test_games(http_client: T_client):
    async with http_client.get("/games/guess") as response:
        response.raise_for_status()

    async with http_client.get("/games/chairs") as response:
        response.raise_for_status()
