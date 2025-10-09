from sqlite3 import Connection

from aiohttp.web import HTTPNoContent, HTTPSeeOther

from raphson_mp.client import RaphsonMusicClient
from raphson_mp.client.track import Track
from raphson_mp.server.auth import User
from tests import T_client, assert_html


async def test_add_remove(
    client: RaphsonMusicClient, http_client: T_client, track: Track, conn: Connection, user: User, csrf_token: str
):
    conn.execute("DELETE FROM dislikes WHERE user = ? AND track = ?", (user.user_id, track.path))

    dislikes = await client.dislikes()
    assert track.path not in dislikes

    async with http_client.post("/dislikes/add", json={"csrf": csrf_token, "track": track.path}) as response:
        assert response.status == HTTPNoContent.status_code

    dislikes = await client.dislikes()
    assert track.path in dislikes

    async with http_client.post(
        "/dislikes/remove", data={"csrf": csrf_token, "track": track.path}, allow_redirects=False
    ) as response:
        assert response.status == HTTPSeeOther.status_code

    dislikes = await client.dislikes()
    assert track.path not in dislikes


async def test_dislikes_page(http_client: T_client):
    await assert_html(http_client, "/dislikes")
