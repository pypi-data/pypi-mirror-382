import base64
import json
import secrets
from sqlite3 import Connection
from typing import cast

from aiohttp import web
from yarl import URL

from raphson_mp.server import auth, cache, i18n, playlist
from raphson_mp.server.decorators import route
from raphson_mp.server.response import template
from raphson_mp.server.theme import THEMES


@route("")
async def route_account(_request: web.Request, conn: Connection, user: auth.User):
    """
    Account information page
    """
    from raphson_mp.server import lastfm

    sessions = user.sessions()

    result = conn.execute("SELECT name FROM user_lastfm WHERE user=?", (user.user_id,)).fetchone()
    if result:
        (lastfm_name,) = result
    else:
        lastfm_name = None

    playlists = playlist.get_playlists(conn, user)

    webauthn_challenge = secrets.token_urlsafe()
    cache.memory_store("webauthn" + webauthn_challenge, b"", 15 * 60)

    return await template(
        "account.jinja2",
        languages=i18n.ALL_LANGUAGE_CODES,
        sessions=sessions,
        lastfm_enabled=lastfm.is_configured(),
        lastfm_name=lastfm_name,
        lastfm_connect_url=lastfm.get_connect_url(),
        playlists=playlists,
        themes=THEMES.items(),
        webauthn_challenge=webauthn_challenge,
        webauthn_identifier=base64.b64encode(str(user.user_id).encode()).decode(),
        webauthn_username=user.username,
        webauthn_displayname=user.nickname if user.nickname else user.username,
    )


@route("/change_settings", method="POST")
async def route_change_settings(request: web.Request, conn: Connection, user: auth.User):
    form = await request.post()
    nickname = form["nickname"]
    lang_code = form["language"]
    privacy = form["privacy"]
    theme = form["theme"]

    if nickname == "":
        nickname = None
    if lang_code == "":
        lang_code = None
    if privacy == "":
        privacy = None

    if lang_code and lang_code not in i18n.ALL_LANGUAGE_CODES:
        raise web.HTTPBadRequest(reason="invalid language code")

    if privacy not in auth.PrivacyOption:
        raise web.HTTPBadRequest(reason="invalid privacy option")

    if theme not in THEMES:
        raise web.HTTPBadRequest(reason="invalid theme")

    conn.execute(
        "UPDATE user SET nickname=?, language=?, privacy=?, theme=? WHERE id=?",
        (nickname, lang_code, privacy, theme, user.user_id),
    )

    raise web.HTTPSeeOther("/account")


@route("/webauthn_setup", method="POST")
async def webauthn_setup(request: web.Request, conn: Connection, user: auth.User):
    received_data = await request.json()

    # https://developer.mozilla.org/en-US/docs/Web/API/AuthenticatorResponse/clientDataJSON
    client_data = json.loads(base64.b64decode(received_data["client"]))
    if client_data["type"] != "webauthn.create":
        raise web.HTTPBadRequest(reason="invalid type")

    # the challenge in client_data is actually base64url-encoded without padding
    # we can safely add == padding, Python will ignore extra padding https://stackoverflow.com/a/49459036
    provided_challenge = base64.urlsafe_b64decode(client_data["challenge"] + "==").decode()
    if cache.memory_get("webauthn" + provided_challenge) is None:
        raise web.HTTPBadRequest(reason="invalid challenge")

    # verify origin
    origin = URL(client_data["origin"])
    if origin.host != request.url.host:
        raise web.HTTPBadRequest(reason=f"origin mismatch {origin.host} | {request.url.host}")

    # public key in DER format
    public_key = base64.b64decode(received_data["public_key"])

    conn.execute(
        """
        INSERT INTO user_webauthn (user, public_key) VALUES (:user, :public_key)
        """,
        {
            "user": user.user_id,
            "public_key": public_key,
        },
    )

    raise web.HTTPNoContent()


@route("/change_password", method="POST")
async def route_change_password(request: web.Request, conn: Connection, user: auth.User):
    """
    Form target to change password, called from /account page
    """
    form = await request.post()
    current_password = cast(str, form["current_password"])
    new_password = cast(str, form["new_password"])

    if not await auth.verify_password(conn, user.user_id, current_password):
        raise web.HTTPBadRequest(reason="incorrect password.")

    await user.update_password(conn, new_password)
    raise web.HTTPSeeOther("/")


@route("/logout", method="POST")
async def route_logout(_request: web.Request, _conn: Connection, _user: auth.User):
    """
    Form target to log out, called from /account page
    """
    # Overwrite token cookie with empty, expired cookie
    response = web.HTTPSeeOther("/")
    response.set_cookie(auth.TOKEN_COOKIE, "", expires="Thu, Jan 01 1970 00:00:00 UTC")
    raise response
