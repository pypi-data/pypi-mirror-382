from raphson_mp.client import RaphsonMusicClient


async def test_search(client: RaphsonMusicClient):
    await client.search("")
    await client.search("hello")


async def test_tags(client: RaphsonMusicClient):
    await client.tags()
