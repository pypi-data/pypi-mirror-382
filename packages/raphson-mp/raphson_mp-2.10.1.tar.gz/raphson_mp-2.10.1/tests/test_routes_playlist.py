from raphson_mp.client import RaphsonMusicClient
from raphson_mp.client.playlist import Playlist
from raphson_mp.common import util
from aiohttp import web
from raphson_mp.server import db
from raphson_mp.server.auth import User

from . import TEST_USERNAME, T_client, assert_html


async def test_stats_page(http_client: T_client):
    await assert_html(http_client, "/playlist/stats")


async def test_share_page(http_client: T_client, playlist: Playlist):
    await assert_html(http_client, "/playlist/share?playlist=" + util.urlencode(playlist.name))


async def test_share_playlist_no_permission(http_client: T_client, playlist: Playlist, user: User, csrf_token: str):
    # not allowed to share playlist if we do not have write access ourselves
    async with http_client.post(
        "/playlist/share", data={"playlist": playlist.name, "username": TEST_USERNAME, "csrf": csrf_token}
    ) as response:
        assert response.status == web.HTTPForbidden.status_code

    with db.MUSIC.connect() as conn:
        assert conn.execute("SELECT * FROM user_playlist_write WHERE user = ?", (user.user_id,)).fetchone() is None


async def test_list(client: RaphsonMusicClient):
    await client.playlists()


async def test_choose_track(client: RaphsonMusicClient, nonempty_playlist: Playlist):
    await client.choose_track(nonempty_playlist)
