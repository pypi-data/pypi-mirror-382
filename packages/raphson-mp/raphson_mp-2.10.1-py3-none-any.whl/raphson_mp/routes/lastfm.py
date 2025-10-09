from sqlite3 import Connection
from typing import cast

from aiohttp import web

from raphson_mp.server import auth, db, response
from raphson_mp.server.decorators import route


@route("/callback", public=True)
async def callback(request: web.Request, _conn: Connection):
    # After allowing access, last.fm sends the user to this page with an
    # authentication token. The authentication token can only be used once,
    # to obtain a session key. Session keys are stored in the database.

    # Cookies are not present here (because of cross-site redirect), so we
    # can't save the token just yet. Add another redirect step.

    auth_token = request.query.get("token")
    assert auth_token
    return await response.template("lastfm_callback.jinja2", auth_token=auth_token)


@route("/connect", method="POST", skip_csrf_check=True)
async def connect(request: web.Request, _conn: Connection, user: auth.User):
    # This form does not have a CSRF token, because the user is not known
    # in the code that serves the form. Not sure how to fix this.

    from raphson_mp.server import lastfm

    auth_token = cast(str, (await request.post())["auth_token"])
    name = await lastfm.obtain_session_key(cast(auth.StandardUser, user), auth_token)

    return await response.template("lastfm_connected.jinja2", name=name)


@route("/disconnect", method="POST")
async def disconnect(_request: web.Request, conn: Connection, user: auth.User):
    with db.MUSIC.connect() as conn:
        conn.execute("DELETE FROM user_lastfm WHERE user=?", (user.user_id,))
    raise web.HTTPSeeOther("/account")
