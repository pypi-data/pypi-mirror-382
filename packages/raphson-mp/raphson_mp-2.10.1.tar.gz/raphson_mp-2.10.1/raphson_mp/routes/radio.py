from sqlite3 import Connection

from aiohttp import web

from raphson_mp.server import radio
from raphson_mp.server.auth import User
from raphson_mp.server.decorators import route
from raphson_mp.server.response import template


@route("/info")
async def route_info(_request: web.Request, conn: Connection, _user: User):
    """
    Endpoint that returns information about the current and next radio track
    """

    current_track = await radio.get_current_track(conn)
    next_track = await radio.get_next_track(conn)
    return web.json_response(
        {
            "current": current_track.track.to_dict(),
            "current_time": current_track.start_time,
            "next": next_track.track.to_dict(),
            "next_time": next_track.start_time,
        }
    )


@route("", redirect_to_login=True)
async def route_radio_home(_request: web.Request, _conn: Connection, _user: User):
    return await template("radio.jinja2")
