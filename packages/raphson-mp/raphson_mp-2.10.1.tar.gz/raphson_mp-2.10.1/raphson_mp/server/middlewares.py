import logging
import sys

from aiohttp import web
from aiohttp.typedefs import Handler
from multidict import CIMultiDictProxy

from raphson_mp.server import auth, response, settings

_LOGGER = logging.getLogger(__name__)


@web.middleware
async def no_cache(request: web.Request, handler: Handler) -> web.StreamResponse:
    response = await handler(request)
    response.headers["Cache-Control"] = "no-cache"
    return response


@web.middleware
async def csp(request: web.Request, handler: Handler) -> web.StreamResponse:
    response = await handler(request)
    # style-src-attr 'self' 'unsafe-inline'; temporarily allowed because of https://github.com/apache/echarts/issues/19570
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; style-src-attr 'self' 'unsafe-inline'; img-src 'self' blob: data:; media-src 'self' blob:; frame-ancestors 'none'; form-action 'self'; base-uri 'none'; report-uri /csp_reports"
    )
    return response


@web.middleware
async def auth_error(request: web.Request, handler: Handler) -> web.StreamResponse:
    """
    Display permission denied error page with reason, or redirect to login page
    """
    try:
        return await handler(request)
    except auth.AuthError as err:
        if err.redirect_to_login:
            raise web.HTTPSeeOther("/auth/login")
        resp = await response.template("403.jinja2", reason=err.reason.message)
        resp.set_status(status=err.reason.http_status)
        return resp


@web.middleware
async def unhandled_error(request: web.Request, handler: Handler) -> web.StreamResponse:
    try:
        return await handler(request)
    except web.HTTPException as ex:
        raise ex
    except Exception:
        _LOGGER.error("Unhandled exception", exc_info=True)
        raise web.HTTPInternalServerError(
            text="Sorry! Cannot continue due to an unhandled exception. The error has been logged. Please contact the server administrator."
        )


@web.middleware
async def profiler(request: web.Request, handler: Handler) -> web.StreamResponse:
    import yappi  # pyright: ignore[reportMissingTypeStubs]

    columns = {0: ("name", 100), 1: ("ncall", 5), 2: ("tsub", 8), 3: ("ttot", 8), 4: ("tavg", 8)}

    yappi.set_clock_type("cpu")  # pyright: ignore[reportUnknownMemberType]
    yappi.start()
    try:
        return await handler(request)
    finally:
        func_stats = yappi.get_func_stats().sort("ttot")  # pyright: ignore[reportUnknownMemberType]
        func_stats._print_header(sys.stdout, columns)  # pyright: ignore[reportUnknownMemberType,reportPrivateUsage]
        for i, stat in enumerate(func_stats):  # pyright: ignore[reportUnknownVariableType]
            stat._print(sys.stdout, columns)  # pyright: ignore[reportUnknownMemberType]
            if i > 10:
                break
        yappi.stop()


"""
proxy_fix middleware based on https://github.com/pgjones/hypercorn/blob/main/src/hypercorn/middleware/proxy_fix.py

Copyright P G Jones 2018.

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""


@web.middleware
async def proxy_fix(request: web.Request, handler: Handler) -> web.StreamResponse:
    client: str | None = None
    headers = request.headers
    if (value := _get_trusted_value("forwarded", headers)) is not None:
        for part in value.split(";"):
            if part.startswith("for="):
                client = part[4:].strip()

    if client is None:
        client = _get_trusted_value("x-forwarded-for", headers)

    if client is not None:
        # The official way is to create a new request object using request.clone(remote=client)
        # But access logs still use the original request object
        # Use this hacky solution instead, perhaps open a PR to aiohttp with a setter for the remote property? (TODO)
        request._cache["remote"] = client  # pyright: ignore[reportPrivateUsage]

    return await handler(request)


def _get_trusted_value(name: str, headers: CIMultiDictProxy[str]) -> str | None:
    trusted_hops = settings.proxy_count
    values: list[str] = []
    for header_name, header_value in headers.items():
        if header_name.lower() == name:
            values.extend([value.strip() for value in header_value.split(",")])
            break
    else:
        return None

    if len(values) == trusted_hops:
        return values[0] if values else None
    else:
        _LOGGER.warning("denied request with invalid proxy headers")
        _LOGGER.warning("someone is attempting to spoof their IP address, or proxy count is not configured correctly")
        raise web.HTTPBadRequest(reason="invalid proxy headers")
