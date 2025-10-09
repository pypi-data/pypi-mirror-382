import logging
import tempfile
from pathlib import Path
from sqlite3 import Connection
from typing import cast

from aiohttp import web

from raphson_mp.server import downloader
from raphson_mp.server.auth import User
from raphson_mp.server.decorators import route
from raphson_mp.server.playlist import Playlist, get_playlists
from raphson_mp.server.response import template

_LOGGER = logging.getLogger(__name__)


@route("", redirect_to_login=True)
async def route_download(_request: web.Request, conn: Connection, user: User):
    return await template("download.jinja2", playlists=get_playlists(conn, user))


@route("/ytdl", method="POST")
async def route_ytdl(request: web.Request, conn: Connection, user: User):
    """
    Use yt-dlp to download the provided URL to a playlist directory
    """
    json = await request.json()
    playlist_name: str = cast(str, json["playlist"])
    url: str = cast(str, json["url"])

    playlist = Playlist(conn, playlist_name, user)
    if not playlist.is_writable:
        raise web.HTTPForbidden(reason="No write permission for this playlist")

    _LOGGER.info("ytdl %s %s", playlist_name, url)

    return web.Response(body=downloader.download(user, playlist, url))


@route("/ephemeral")
async def route_ephemeral(request: web.Request, _conn: Connection, user: User):
    url = request.query.get("url")
    assert url
    with tempfile.TemporaryDirectory() as tempdir:
        temp_path = Path(tempdir)
        async for _log in downloader.download(user, temp_path, url):
            pass
        return web.FileResponse(next(temp_path.iterdir()))
