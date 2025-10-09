import asyncio
import os
import shutil
from pathlib import Path
from sqlite3 import Connection
from typing import cast

from aiohttp import web

from raphson_mp.common import util
from raphson_mp.common.track import MUSIC_EXTENSIONS, TRASH_PREFIX, relpath_playlist
from raphson_mp.server import auth, scanner, settings, track
from raphson_mp.server.decorators import route
from raphson_mp.server.playlist import Playlist, check_path_writable
from raphson_mp.server.response import directory_as_zip, file_attachment, template
from raphson_mp.server.track import from_relpath


def _get_files_url(relpath: str):
    if relpath == "":
        return "/files"
    else:
        return "/files?path=" + util.urlencode(relpath)


@route("", redirect_to_login=True)
async def route_files(request: web.Request, conn: Connection, user: auth.User):
    """
    File manager
    """
    browse_relpath = request.query.get("path", "")
    browse_path = track.from_relpath(browse_relpath)

    show_trashed = "trash" in request.query

    if browse_path == settings.music_dir:
        back_url = "/"
        write_permission = user.admin
    else:
        back_url = _get_files_url(os.path.dirname(browse_relpath))
        playlist = Playlist(conn, relpath_playlist(browse_relpath), user)
        write_permission = playlist.is_writable

    children: list[dict[str, str]] = []

    # iterdir() is slow and blocking, so must be run in a separate thread
    def thread():
        for path in browse_path.iterdir():
            if track.is_trashed(path) != show_trashed:
                continue

            relpath = track.to_relpath(path)

            children.append(
                {
                    "path": relpath,
                    "displayname": path.name[len(TRASH_PREFIX) :] if show_trashed else path.name,
                    "type": "d" if path.is_dir() else "f",
                }
            )

    await asyncio.to_thread(thread)

    # go back to main thread to use database connection
    for child in children:
        if child["type"] == "dir":
            continue

        row = conn.execute(
            """
            SELECT title, GROUP_CONCAT(artist, ", ")
            FROM track LEFT JOIN track_artist ON path = track
            WHERE path = ?
            GROUP BY path
            """,
            (child["path"],),
        ).fetchone()

        if row:
            title, artists = row
            child["type"] = "m"
            child["title"] = title if title else ""
            child["artist"] = artists if artists else ""

    # Sort directories first, and ignore case for file name
    def sort_name(obj: dict[str, str]) -> str:
        return ("a" if obj["type"] == "d" else "b") + obj["displayname"].lower()

    children = sorted(children, key=sort_name)

    return await template(
        "files.jinja2",
        base_path=browse_relpath,
        base_url=_get_files_url(browse_relpath),
        back_url=back_url,
        write_permission=write_permission,
        files=children,
        music_extensions=",".join(MUSIC_EXTENSIONS),
        show_trashed=show_trashed,
    )


@route("/upload", method="POST")
async def route_upload(request: web.Request, conn: Connection, user: auth.User):
    """
    Form target to upload file, called from file manager
    """
    form = await request.post()

    relpath = cast(str, form["dir"])
    upload_dir: Path = track.from_relpath(relpath)

    playlist_to_scan = None

    for uploaded_file in cast(list[web.FileField], form.getall("upload")):
        path = Path(upload_dir, uploaded_file.filename)

        playlist_to_scan = check_path_writable(conn, user, path)

        with path.open("wb") as fp:
            while data := uploaded_file.file.read(1024 * 1024):
                fp.write(data)

    if playlist_to_scan:
        util.create_task(scanner.scan_playlist(user, playlist_to_scan))

    raise web.HTTPSeeOther(_get_files_url(relpath))


@route("/rename")
async def route_rename_get(request: web.Request, _conn: Connection, _user: auth.User):
    path = request.query["path"]
    back_url = _get_files_url(os.path.dirname(path))
    return await template("files_rename.jinja2", path=path, name=path.split("/")[-1], back_url=back_url)


@route("/rename", method="POST")
async def route_rename_post(request: web.Request, conn: Connection, user: auth.User):
    if request.content_type == "application/json":
        json = await request.json()
        relpath = cast(str, json["path"])
        new_name = cast(str, json["new_name"])
    else:
        form = await request.post()
        relpath = cast(str, form["path"])
        new_name = cast(str, form["new-name"])

    path = track.from_relpath(relpath)
    new_path = Path(path.parent, new_name)

    playlist1 = check_path_writable(conn, user, path)
    playlist2 = check_path_writable(conn, user, new_path)
    assert playlist1 == playlist2

    await scanner.move(user, path, new_path)

    if request.content_type == "application/json":
        raise web.HTTPNoContent()

    raise web.HTTPSeeOther(_get_files_url(os.path.dirname(relpath)))


@route("/mkdir", method="POST")
async def route_mkdir(request: web.Request, conn: Connection, user: auth.User):
    """
    Create directory, then enter it
    """
    form = await request.post()
    relpath = cast(str, form["path"])
    dirname = cast(str, form["dirname"])

    parent = track.from_relpath(relpath)

    if relpath == "":
        to_create = Path(parent, dirname)

        # Creating a root playlist directory
        if to_create.exists():
            raise web.HTTPBadRequest(reason="Playlist path already exists")

        to_create.mkdir()

        # This creates a row for the playlist in the playlist table
        await scanner.scan_playlists()

        # New playlist should be writable for user who created it
        conn.execute("INSERT INTO user_playlist_write VALUES (?, ?)", (user.user_id, dirname))
    else:
        # Creating a directory inside an existing playlist
        playlist = Playlist(conn, relpath_playlist(relpath), user)
        if not playlist.is_writable:
            raise web.HTTPForbidden(reason="No write permission for this playlist")

        to_create = Path(parent, dirname)
        to_create.mkdir()

    raise web.HTTPSeeOther("/files?path=" + util.urlencode(track.to_relpath(to_create)))


@route("/download")
async def route_download(request: web.Request, _conn: Connection, _user: auth.User):
    """
    Download single file
    """
    path = track.from_relpath(request.query["path"])
    if path.is_dir():
        return directory_as_zip(path)

    if path.is_file():
        return file_attachment(path)

    raise web.HTTPBadRequest()


@route("/copy", method="POST")
async def route_copy_track(request: web.Request, conn: Connection, user: auth.User):
    # Used by music player from javascript
    json = await request.json()

    src = cast(str, json["src"])
    dest = cast(str, json["dest"])

    src_path = from_relpath(src)
    dest_path = Path(from_relpath(dest), src_path.name)

    dest_playlist = check_path_writable(conn, user, dest_path)

    await asyncio.to_thread(shutil.copy, src_path, dest_path)

    util.create_task(scanner.scan_playlist(user, dest_playlist))

    raise web.HTTPNoContent()
