import time
from sqlite3 import Connection
from typing import cast

from aiohttp import web

from raphson_mp.server.auth import User
from raphson_mp.server.decorators import route
from raphson_mp.server.i18n import format_timedelta
from raphson_mp.server.i18n import gettext as _
from raphson_mp.server.response import template


@route("", redirect_to_login=True, require_admin=True)
async def route_users(_request: web.Request, conn: Connection, _user: User):
    """User list page"""
    result = conn.execute(
        """
        SELECT user.id, username, admin, primary_playlist, MAX(last_use)
        FROM user LEFT JOIN session ON user.id = session.user
        GROUP BY user.id
        """
    )
    users = [
        {
            "id": user_id,
            "username": username,
            "admin": admin,
            "primary_playlist": primary_playlist,
            "last_use": last_use,
        }
        for user_id, username, admin, primary_playlist, last_use in result
    ]

    for user_dict in users:
        result = conn.execute("SELECT playlist FROM user_playlist_write WHERE user=?", (user_dict["id"],))
        user_dict["writable_playlists"] = [playlist for playlist, in result]
        user_dict["writable_playlists_str"] = ", ".join(user_dict["writable_playlists"])
        if user_dict["last_use"] is None:
            user_dict["last_use"] = _("More than 30 days ago")
        else:
            user_dict["last_use"] = format_timedelta(user_dict["last_use"] - int(time.time()), add_direction=True)

    return await template("users.jinja2", users=users)


@route("/edit", require_admin=True)
async def route_edit_get(request: web.Request, _conn: Connection, _user: User):
    """Change username or password"""
    username = request.query["username"]

    return await template("users_edit.jinja2", username=username)


@route("/edit", method="POST", require_admin=True)
async def route_edit_post(request: web.Request, conn: Connection, _user: User):
    form = await request.post()
    username = cast(str, form["username"])
    new_username = cast(str, form["new_username"])
    new_password = cast(str, form["new_password"])

    (user_id,) = conn.execute("SELECT id FROM user WHERE username=?", (username,)).fetchone()
    target_user = User.get(conn, user_id=user_id)

    if new_password != "":
        await target_user.update_password(conn, new_password)

    if new_username != username:
        await target_user.update_username(conn, new_username)

    raise web.HTTPSeeOther("/users")


@route("/new", method="POST", require_admin=True)
async def route_new(request: web.Request, conn: Connection, _user: User):
    """Create new user"""
    form = await request.post()
    username = cast(str, form["username"])
    password = cast(str, form["password"])
    await User.create(conn, username, password)
    raise web.HTTPSeeOther("/users")
