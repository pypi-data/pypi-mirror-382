import asyncio
import os
from sqlite3 import Connection
import tempfile

from aiohttp import hdrs, web

from raphson_mp.common.io_response import IOResponse
from raphson_mp.common.track import NoSuchTrackError
from raphson_mp.server import auth, db
from raphson_mp.server.decorators import route
from raphson_mp.server.track import FileTrack


@route("/{relpath}/info")
async def route_info(request: web.Request, conn: Connection, _user: auth.User):
    relpath = request.match_info["relpath"]
    try:
        track = FileTrack(conn, relpath)
    except NoSuchTrackError:
        raise web.HTTPNotFound(reason="track not found")

    return web.json_response(track.to_dict())


@route("/{relpath}/audio")
async def route_audio(request: web.Request, _conn: Connection, _user: auth.User):
    relpath = request.match_info["relpath"]
    with db.OFFLINE.connect() as conn_offline:
        music_data: bytes = conn_offline.execute(
            """SELECT music_data FROM content WHERE path=?""", (relpath,)
        ).fetchone()[0]
        fd, path = tempfile.mkstemp()
        fp = os.fdopen(fd, "wb")
        await asyncio.to_thread(fp.write, music_data)
        os.unlink(path) # file will be deleted when file descriptor is closed
        return IOResponse(fp, headers={hdrs.CONTENT_TYPE: "audio/webm"})


@route("/{relpath}/cover")
async def route_album_cover(request: web.Request, _conn: Connection, _user: auth.User):
    relpath = request.match_info["relpath"]
    with db.OFFLINE.connect() as conn_offline:
        cover_data: bytes = conn_offline.execute(
            """SELECT cover_data FROM content WHERE path=?""", (relpath,)
        ).fetchone()[0]
        return web.Response(body=cover_data, content_type="image/webp")
