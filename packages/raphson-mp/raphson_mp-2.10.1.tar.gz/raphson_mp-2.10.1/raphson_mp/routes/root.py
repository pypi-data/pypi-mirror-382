from __future__ import annotations

import json
import logging
from sqlite3 import Connection

from aiohttp import web

from raphson_mp.common import const, util
from raphson_mp.server import auth, ratelimit, response, features
from raphson_mp.server.decorators import route, simple_route

log = logging.getLogger(__name__)


@route("", redirect_to_login=True)
async def route_home(_request: web.Request, _conn: Connection, user: auth.User):
    """
    Home page, with links to file manager and music player
    """
    return await response.template(
        "home.jinja2",
        user_is_admin=user.admin,
        version=const.PACKAGE_VERSION,
        Feature=features.Feature,
        features=features.FEATURES,
    )


@route("/install")
async def route_install(_request: web.Request, _conn: Connection, _user: auth.User):
    return await response.template("install.jinja2")


@simple_route("/pwa")
async def route_pwa(_request: web.Request):
    # Cannot have / as an entrypoint directly, because for some reason the first request
    # to the start_url does not include cookies. Even a regular 302 redirect doesn't work!
    return web.Response(text='<meta http-equiv="refresh" content="0;URL=\'/player\'">', content_type="text/html")


@simple_route("/csp_reports", method="POST")
async def route_csp_reports(request: web.Request):
    if request.content_type != "application/csp-report":
        raise web.HTTPBadRequest(reason="Content-Type must be application/csp-report")

    async with ratelimit.ERROR_REPORT:
        data = await util.get_content_bounded(request)
        log.warning("Received Content-Security-Policy report: %s", json.loads(data))

    raise web.HTTPNoContent()


@simple_route("/report_error", method="POST")
async def route_error_report(request: web.Request):
    async with ratelimit.ERROR_REPORT:
        data = await util.get_content_bounded(request)
        log.warning("Received JavaScript error: %s", data)

    raise web.HTTPNoContent()


# TODO add nice interface
# TODO add a way to discover this page
# TODO require user password
@route("/token")
async def route_token(request: web.Request, conn: Connection, user: auth.User):
    session = await auth.create_session(conn, request, user)
    return web.Response(text=session.token)


@simple_route("/health_check")
async def route_health_check(_request: web.Request):
    return web.Response(text="ok", content_type="text/plain")


@simple_route("/.well-known/security.txt")
async def security_txt(_request: web.Request):
    content = """Contact: mailto:robin@rslot.nl
Expires: 2026-06-01T23:59:59.000Z
Preferred-Languages: nl, en
"""
    return web.Response(text=content, content_type="text/plain")
