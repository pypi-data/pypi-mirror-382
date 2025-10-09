import base64
import hashlib
import json
import logging
import secrets
from sqlite3 import Connection
from typing import cast

from aiohttp import web
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ec import ECDSA, EllipticCurvePublicKey
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.serialization import load_der_public_key
from yarl import URL

from raphson_mp.server import auth, cache
from raphson_mp.server.auth import AuthError, User
from raphson_mp.server.decorators import route
from raphson_mp.server.response import template

log = logging.getLogger(__name__)


@route("/login", public=True)
async def route_login_get(request: web.Request, conn: Connection):
    try:
        await auth.verify_auth_cookie(conn, request)
        # User is already logged in
        raise web.HTTPSeeOther("/")
    except AuthError:
        pass

    (user_count,) = conn.execute("SELECT COUNT(*) FROM user").fetchone()
    if user_count == 0:
        return await template("login_noaccounts.jinja2")

    webauthn_challenge = secrets.token_urlsafe()
    cache.memory_store("webauthn" + webauthn_challenge, b"", 15 * 60)
    return await template("login.jinja2", invalid_password=False, webauthn_challenge=webauthn_challenge)


@route("/login", method="POST", public=True)
async def route_login_post(request: web.Request, conn: Connection):
    if request.content_type == "application/json":
        data = await request.json()
    else:
        data = await request.post()
    username: str = cast(str, data["username"])
    password: str = cast(str, data["password"])

    session = await auth.log_in(request, conn, username, password)

    if session is None:
        if request.content_type == "application/json":
            raise web.HTTPForbidden()

        webauthn_challenge = secrets.token_urlsafe()
        cache.memory_store("webauthn" + webauthn_challenge, b"", 15 * 60)
        return await template("login.jinja2", invalid_password=True, webauthn_challenge=webauthn_challenge)

    if request.content_type == "application/json":
        return web.json_response({"token": session.token, "csrf": session.csrf_token})

    response = web.HTTPSeeOther("/")
    session.set_cookie(response)
    raise response


@route("/get_csrf")
async def route_get_csrf(_request: web.Request, _conn: Connection, user: User):
    """
    Get CSRF token
    """
    return web.json_response({"token": user.csrf})


@route("/webauthn_login", method="POST", public=True, skip_csrf_check=True)
async def webauthn_login(request: web.Request, conn: Connection):
    data = await request.json()
    authenticator_data = base64.b64decode(data["authenticator_data"])
    client_data_bytes = base64.b64decode(data["client_data"])
    client_data = json.loads(client_data_bytes)
    signature = base64.b64decode(data["signature"])
    user_handle = base64.b64decode(data["user_handle"])

    log.debug("authenticator_data: %s", authenticator_data)
    log.debug("client_data: %s", client_data)
    log.debug("signature: %s", signature)
    log.debug("user_handle: %s", user_handle)

    user_id = int(user_handle.decode())
    log.debug("user_id: %s", user_id)

    # verify clientData type
    assert client_data["type"] == "webauthn.get"

    # verify clientData origin
    origin = URL(client_data["origin"])
    if origin.host != request.url.host:
        raise web.HTTPBadRequest(reason=f"origin mismatch {origin.host} | {request.url.host}")

    # verify clientData challenge
    provided_challenge = base64.urlsafe_b64decode(client_data["challenge"] + "==").decode()
    if cache.memory_get("webauthn" + provided_challenge) is None:
        log.warning("webauthn login attempt with invalid challenge")
        raise web.HTTPBadRequest(reason="invalid challenge")

    public_keys = [
        row[0]
        for row in conn.execute(
            "SELECT public_key FROM user_webauthn WHERE user = ?",
            (user_id,),
        )
    ]

    for public_key in public_keys:
        public_key = cast(EllipticCurvePublicKey, load_der_public_key(public_key))
        print(authenticator_data)
        print(client_data_bytes)
        signed_data = authenticator_data + hashlib.sha256(client_data_bytes).digest()

        try:
            public_key.verify(signature, signed_data, ECDSA(SHA256()))
            log.info("successful login using webauthn")
            session = await auth.create_session(conn, request, user_id)
            response = web.HTTPNoContent()
            session.set_cookie(response)
            raise response
        except InvalidSignature:
            continue

    if public_keys:
        log.warning("attempted webauthn login, but no public keys matched")
    else:
        log.warning("attempted webauthn login, but no public keys are stored")

    raise web.HTTPBadRequest(reason="invalid signature")
