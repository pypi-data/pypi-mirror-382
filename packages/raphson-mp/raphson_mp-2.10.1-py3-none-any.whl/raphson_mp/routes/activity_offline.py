from sqlite3 import Connection
from typing import cast

from aiohttp import web

from raphson_mp.server import auth, db
from raphson_mp.server.decorators import route


@route("/played", method="POST")
async def route_played(request: web.Request, _conn: Connection, _user: auth.User):
    json = await request.json()
    track = cast(str, json["track"])
    timestamp = cast(int, json["timestamp"])
    with db.OFFLINE.connect() as conn_offline:
        conn_offline.execute("INSERT INTO history VALUES (?, ?)", (timestamp, track))
    raise web.HTTPNoContent()
