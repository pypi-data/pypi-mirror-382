from sqlite3 import Connection
from typing import cast

from aiohttp import web

from raphson_mp.common.typing import DislikesResponseDict
from raphson_mp.server.auth import User
from raphson_mp.server.decorators import route
from raphson_mp.server.response import template
from raphson_mp.server.track import FileTrack


@route("/add", method="POST")
async def route_add(request: web.Request, conn: Connection, user: User):
    """Used by music player"""
    json = await request.json()
    track_path = cast(str, json["track"])
    conn.execute("INSERT OR IGNORE INTO dislikes (user, track) VALUES (?, ?)", (user.user_id, track_path))
    raise web.HTTPNoContent()


@route("/remove", method="POST")
async def route_remove(request: web.Request, conn: Connection, user: User):
    """Used by form on dislikes page"""
    form = await request.post()
    relpath = cast(str, form["track"])
    conn.execute("DELETE FROM dislikes WHERE user=? AND track=?", (user.user_id, relpath))
    raise web.HTTPSeeOther("/dislikes")


@route("")
async def route_dislikes(_request: web.Request, conn: Connection, user: User):
    """
    Page showing a table with disliked tracks, with buttons to undo disliking each trach.
    """
    tracks = [
        FileTrack(conn, row[0]) for row in conn.execute("SELECT track FROM dislikes WHERE user=?", (user.user_id,))
    ]
    return await template("dislikes.jinja2", tracks=tracks)


@route("/json")
async def route_json(_request: web.Request, conn: Connection, user: User):
    """
    Return disliked track paths in json format, for offline mode sync
    """
    rows = conn.execute("SELECT track FROM dislikes WHERE user=?", (user.user_id,))
    response_dict: DislikesResponseDict = {"tracks": [row[0] for row in rows]}
    return web.json_response(response_dict)
