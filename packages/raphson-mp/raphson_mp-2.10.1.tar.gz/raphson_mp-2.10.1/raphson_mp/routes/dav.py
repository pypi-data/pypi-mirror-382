import asyncio
import logging
import shutil
import xml.etree.ElementTree as ET
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from sqlite3 import Connection
from urllib.parse import quote

from aiohttp import web
from yarl import URL

from raphson_mp.common import util
from raphson_mp.common.track import TRASH_PREFIX
from raphson_mp.server import auth, db, scanner, track
from raphson_mp.server.auth import AuthError, User
from raphson_mp.server.decorators import Route, simple_route
from raphson_mp.server.playlist import check_path_writable

# Main WebDAV RFC, often referred to in this file: https://www.ietf.org/rfc/rfc4918.txt

_LOGGER = logging.getLogger(__name__)
DAV_BASE = "/dav/"

DavHandler = Callable[[web.Request, Connection, User, str], Awaitable[web.StreamResponse]]


def dav_route(method: str) -> Callable[[DavHandler], Route]:
    def decorator(handler: DavHandler) -> Route:
        async def wrapper(request: web.Request) -> web.StreamResponse:
            with db.MUSIC.connect() as conn:
                try:
                    user = await auth.verify_auth_cookie(conn, request)
                except AuthError:
                    raise web.HTTPUnauthorized(headers={"WWW-Authenticate": 'Basic realm="Music player WebDAV"'})
                relpath = request.match_info["path"].rstrip("/") if "path" in request.match_info else ""
                return await handler(request, conn, user, relpath)

        return Route(
            [
                web.route(method, "/{path:.*}", wrapper),
                web.route(method, "", wrapper),
            ]
        )

    return decorator


# required by Nautilus and perhaps other file managers
# see RFC 4918 sections 10.1 and 18
@simple_route("", "/{any:.*}", method="OPTIONS")
async def options(_request: web.Request):
    raise web.HTTPOk(headers={"DAV": "1, 3"})


def xml_response(element: ET.Element, status: int = 200):
    return web.Response(
        body=b'<?xml version="1.0" encoding="utf-8" ?>' + ET.tostring(element),
        content_type="application/xml",
        status=status,
    )


def _propfind_response(path: Path, include_quota: bool = False):
    stat = path.stat()
    xresponse = ET.Element("d:response")

    xhref = ET.Element("d:href")
    xhref.text = DAV_BASE + track.to_relpath(path)
    if path.is_dir():
        xhref.text = xhref.text.rstrip("/") + "/"
    # URI must be urlencoded, see RFC 4918 section 8.3.1
    xhref.text = quote(xhref.text)
    xresponse.append(xhref)

    xpropstat = ET.Element("d:propstat")
    xstatus = ET.Element("d:status")
    xstatus.text = "HTTP/1.1 200 OK"
    xpropstat.append(xstatus)
    xprop = ET.Element("d:prop")

    xgetlastmodified = ET.Element("d:getlastmodified")
    xgetlastmodified.text = format_datetime(datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc))
    xprop.append(xgetlastmodified)

    if path.is_dir():
        xresourcetype = ET.Element("d:resourcetype")
        xcollection = ET.Element("d:collection")
        xresourcetype.append(xcollection)
        xprop.append(xresourcetype)
    else:
        xresourcetype = ET.Element("d:resourcetype")
        xprop.append(xresourcetype)

        xgetcontentlength = ET.Element("d:getcontentlength")
        xgetcontentlength.text = str(stat.st_size)
        xprop.append(xgetcontentlength)

    if include_quota:
        # RFC 4331
        _total, used, free = shutil.disk_usage(path)
        xquota_available_bytes = ET.Element("d:quota-available-bytes")
        xquota_available_bytes.text = str(free)
        xprop.append(xquota_available_bytes)
        xquota_used_bytes = ET.Element("d:quota-used-bytes")
        xquota_used_bytes.text = str(used)
        xprop.append(xquota_used_bytes)

    xpropstat.append(xprop)
    xresponse.append(xpropstat)

    return xresponse


@dav_route("PROPFIND")
async def propfind(request: web.Request, _conn: Connection, _user: User, relpath: str):
    depth = request.headers.get("Depth", "1")
    if depth not in {"0", "1"}:
        raise web.HTTPBadRequest(reason="unsupported depth")

    def thread():
        path = track.from_relpath(relpath)
        if not path.exists():
            raise web.HTTPNotFound()

        xmultistatus = ET.Element("d:multistatus")
        xmultistatus.set("xmlns:d", "DAV:")

        # path itself is always included
        xmultistatus.append(_propfind_response(path, include_quota=True))

        # if this a directory, include children if requested
        if depth == "1" and path.is_dir():
            for entry in path.iterdir():
                if track.is_trashed(entry):
                    continue
                xmultistatus.append(_propfind_response(entry))

        return xmultistatus

    return xml_response(await asyncio.to_thread(thread), status=207)


@dav_route("GET")
async def get(_request: web.Request, _conn: Connection, _user: User, relpath: str):
    path = track.from_relpath(relpath)
    if not path.exists():
        raise web.HTTPNotFound()
    if not path.is_file():
        raise web.HTTPBadRequest()  # TODO is this the correct response?
    return web.FileResponse(path)


@dav_route("PUT")
async def put(request: web.Request, conn: Connection, user: User, relpath: str):
    path = track.from_relpath(relpath)
    check_path_writable(conn, user, path)

    # file should not already exist
    if path.exists():
        raise web.HTTPMethodNotAllowed("PUT", ["GET", "PROPFIND"])

    # write file to .part file first, so it is ignored if a scanner runs while the file is uploading
    # when the upload is done, rename it
    temp_path = Path(path.parent, path.name + ".part")
    if temp_path.exists():
        temp_path.unlink()

    with temp_path.open("wb") as dest_file:
        while data := await request.content.read(10 * 1024 * 1024):
            await asyncio.to_thread(dest_file.write, data)

    await asyncio.to_thread(temp_path.rename, path)

    # scan for changes
    util.create_task(scanner.scan_track(user, path))

    raise web.HTTPCreated()


@dav_route("DELETE")
async def delete(_request: web.Request, conn: Connection, user: User, relpath: str):
    path = track.from_relpath(relpath)

    # file to delete must exist
    if not path.exists():
        raise web.HTTPMethodNotAllowed("DELETE", [])

    check_path_writable(conn, user, path)

    # delete file
    await asyncio.to_thread(path.rename, Path(path.parent, TRASH_PREFIX + path.name))

    # scan for changes
    util.create_task(scanner.scan_track(user, path))

    raise web.HTTPNoContent()


@dav_route("MKCOL")
async def mkcol(request: web.Request, conn: Connection, user: User, relpath: str):
    if request.content_length and request.content_length > 0:
        raise web.HTTPUnsupportedMediaType()

    path = track.from_relpath(relpath)
    check_path_writable(conn, user, path)
    if not path.parent.is_dir():
        raise web.HTTPConflict()
    if path.is_dir():
        raise web.HTTPConflict()

    await asyncio.to_thread(path.mkdir)

    raise web.HTTPCreated()


@dav_route("MOVE")
async def move(request: web.Request, conn: Connection, user: User, from_relpath: str):
    # obtain relpaths
    to_uri = request.headers["Destination"]
    to_uri_path = URL(to_uri).path
    if not to_uri_path.startswith(DAV_BASE):
        _LOGGER.warning("destination does not start with DAV_BASE: %s", to_uri)
        raise web.HTTPBadRequest(reason="destination must start with: " + DAV_BASE)
    to_relpath = to_uri_path[len(DAV_BASE) :]

    from_path = track.from_relpath(from_relpath)
    to_path = track.from_relpath(to_relpath)

    # verify write permission
    check_path_writable(conn, user, from_path)
    check_path_writable(conn, user, to_path)

    # source should exist
    if not from_path.exists():
        _LOGGER.warning("path does not exist: %s", from_path.as_posix())
        raise web.HTTPMethodNotAllowed("MOVE", ["GET", "PROPFIND"])

    # destination parent should exist
    if not to_path.parent.exists():
        raise web.HTTPConflict(reason="parent directory must be created first")

    # destination should not exist if overwrites are not allowed
    if request.headers.get("Overwrite", "F") != "T" and to_path.exists():
        raise web.HTTPPreconditionFailed(reason="destination already exists")

    # actually perform move
    await scanner.move(user, from_path, to_path)

    raise web.HTTPNoContent()
