from sqlite3 import Connection

from aiohttp import web

from raphson_mp.server.auth import User
from raphson_mp.server.decorators import route
from raphson_mp.server.response import template
from raphson_mp.server.track import FileTrack


@route("")
async def problems(_request: web.Request, conn: Connection, _user: User):
    tracks = [FileTrack(conn, row[0]) for row in conn.execute("SELECT track FROM track_problem")]
    return await template("problems.jinja2", tracks=tracks)


@route("/undo", method="POST")
async def undo(request: web.Request, conn: Connection, _user: User):
    relpath = (await request.post())["path"]
    conn.execute("DELETE FROM track_problem WHERE track = ?", (relpath,))
    raise web.HTTPSeeOther("/problems")
