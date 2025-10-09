from aiohttp.web import HTTPForbidden

from raphson_mp.client.playlist import Playlist

from . import T_client


async def test_download_no_permission(http_client: T_client, csrf_token: str, playlist: Playlist):
    async with http_client.post(
        "/download/ytdl", json={"csrf": csrf_token, "playlist": playlist.name, "url": ""}
    ) as response:
        assert response.status == HTTPForbidden.status_code
