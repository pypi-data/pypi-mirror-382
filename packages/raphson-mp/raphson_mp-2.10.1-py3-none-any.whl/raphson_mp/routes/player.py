from sqlite3 import Connection

from aiohttp import web

from raphson_mp.common import util
from raphson_mp.common.lyrics import INSTRUMENTAL_TEXT
from raphson_mp.server.auth import StandardUser, User
from raphson_mp.server.decorators import route
from raphson_mp.server.response import template


@route("", redirect_to_login=True)
async def route_player(request: web.Request, _conn: Connection, user: User):
    """
    Main player page. Serves player.jinja2 template file.
    """
    response = await template(
        "player.jinja2",
        mobile=util.is_mobile(request),
        instrumental=INSTRUMENTAL_TEXT,
    )

    # Refresh token cookie
    if isinstance(user, StandardUser):
        assert user.session
        user.session.set_cookie(response)

    return response
