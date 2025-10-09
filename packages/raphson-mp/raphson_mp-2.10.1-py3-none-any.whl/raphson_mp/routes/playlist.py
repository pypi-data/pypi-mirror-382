from __future__ import annotations

import asyncio
from sqlite3 import Connection
from typing import cast

from aiohttp import web

from raphson_mp.common.tag import TagMode
from raphson_mp.common.typing import PlaylistDict
from raphson_mp.server.auth import User
from raphson_mp.server.decorators import route
from raphson_mp.server.playlist import Playlist, PlaylistStats, get_playlists
from raphson_mp.server.response import template


@route("/stats")
async def route_stats(_request: web.Request, conn: Connection, user: User):
    playlists_stats: list[PlaylistStats] = []
    for playlist in get_playlists(conn):
        await asyncio.sleep(0)  # yield to event loop
        playlists_stats.append(playlist.stats(conn))

    return await template(
        "playlists_stats.jinja2",
        user_is_admin=user.admin,
        playlists_stats=playlists_stats,
    )


@route("/share")
async def route_share_get(request: web.Request, conn: Connection, _user: User):
    """
    Page to select a username to share the provided playlist with
    """
    usernames = [row[0] for row in conn.execute("SELECT username FROM user")]
    playlist_relpath = request.query["playlist"]
    return await template("playlists_share.jinja2", playlist=playlist_relpath, usernames=usernames)


@route("/share", method="POST")
async def route_share_post(request: web.Request, conn: Connection, user: User):
    """
    Form target to submit the selected username
    """
    form = await request.post()
    playlist_name = cast(str, form["playlist"])
    username = cast(str, form["username"])

    (target_user_id,) = conn.execute("SELECT id FROM user WHERE username=?", (username,)).fetchone()

    # Verify playlist exists and user has write access
    playlist = Playlist(conn, playlist_name, user)
    if not playlist.is_writable:
        raise web.HTTPForbidden(reason="Cannot share playlist if you do not have write permission")

    conn.execute("INSERT INTO user_playlist_write VALUES(?, ?) ON CONFLICT DO NOTHING", (target_user_id, playlist_name))
    raise web.HTTPSeeOther("/playlist/manage")


@route("/list")
async def route_list(_request: web.Request, conn: Connection, user: User):
    playlists = get_playlists(conn, user)
    json: list[PlaylistDict] = [
        {
            "name": playlist.name,
            "track_count": playlist.track_count,
            "favorite": playlist.is_favorite,
            "write": playlist.is_writable,
        }
        for playlist in playlists
    ]
    return web.json_response(json)


@route("/{playlist}/choose_track", method="POST")
async def route_track(request: web.Request, conn: Connection, user: User):
    """
    Choose random track from the provided playlist directory.
    """
    playlist_name = request.match_info["playlist"]
    playlist = Playlist(conn, playlist_name)
    json = await request.json()
    require_metadata: bool = cast(bool, json["require_metadata"]) if "require_metadata" in json else False

    if "tag_mode" in json:
        tag_mode = TagMode(cast(str, json["tag_mode"]))
        tags = cast(list[str], json["tags"])
        chosen_track = await playlist.choose_track(
            conn, user, require_metadata=require_metadata, tag_mode=tag_mode, tags=tags
        )
    else:
        chosen_track = await playlist.choose_track(conn, user, require_metadata=require_metadata)

    if chosen_track is None:
        raise web.HTTPNotFound(reason="no track found")

    return web.json_response(chosen_track.to_dict())
