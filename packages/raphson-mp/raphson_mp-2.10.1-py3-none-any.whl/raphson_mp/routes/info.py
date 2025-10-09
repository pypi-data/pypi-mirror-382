from sqlite3 import Connection

from aiohttp import web

from raphson_mp.server.auth import User
from raphson_mp.server.decorators import route
from raphson_mp.server.features import FEATURES, Feature
from raphson_mp.server.response import template


@route("")
async def route_info(_request: web.Request, _conn: Connection, _user: User):
    """
    Information/manual page
    """
    return await template("info.jinja2", webdav=Feature.WEBDAV in FEATURES, subsonic=Feature.SUBSONIC in FEATURES)
