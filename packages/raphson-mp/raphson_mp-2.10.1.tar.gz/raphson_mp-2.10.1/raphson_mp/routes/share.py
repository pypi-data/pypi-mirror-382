import os
import time
from base64 import b32encode
from sqlite3 import Connection
from typing import cast

from aiohttp import web

from raphson_mp.common.image import ImageFormat, ImageQuality
from raphson_mp.common.lyrics import ensure_plain
from raphson_mp.common.track import AudioFormat
from raphson_mp.server import blob
from raphson_mp.server.auth import User
from raphson_mp.server.decorators import route
from raphson_mp.server.response import template
from raphson_mp.server.track import FileTrack


def gen_share_code() -> str:
    """
    Generate new random share code
    """
    return b32encode(os.urandom(8)).decode().lower().rstrip("=")


def track_from_url(conn: Connection, request: web.Request) -> FileTrack:
    """
    Find track using a provided share code
    """
    share_code = request.match_info["share_code"]
    track_code = request.match_info["track_code"]
    row = conn.execute(
        "SELECT track FROM share_track WHERE share_code=? AND track_code = ?", (share_code, track_code)
    ).fetchone()
    if row is None:
        raise web.HTTPNotFound(reason="no share was found with the given code")

    return FileTrack(conn, row[0])


@route("/create", method="POST")
async def create(request: web.Request, conn: Connection, user: User):
    """
    Endpoint to create a share link, called from web music player and playlist manager
    """
    if request.content_type == "application/json":
        data = await request.json()
    else:
        data = await request.post()

    if "track" in data:
        # sharing a single track
        relpath = cast(str, data["track"])
        track = FileTrack(conn, relpath)
        relpaths = [track.path]
    elif "playlist" in data:
        # sharing a playlist
        playlist_name = cast(str, data["playlist"])
        relpaths = [row[0] for row in conn.execute("SELECT path FROM track WHERE playlist = ?", (playlist_name,))]
    else:
        raise web.HTTPBadRequest()

    share_code = gen_share_code()

    # create share
    conn.execute(
        "INSERT INTO share (share_code, user, create_timestamp) VALUES (?, ?, ?)",
        (share_code, user.user_id, int(time.time())),
    )

    # add tracks to share
    for relpath in relpaths:
        conn.execute(
            "INSERT INTO share_track (share_code, track_code, track) VALUES (?, ?, ?)",
            (share_code, gen_share_code(), relpath),
        )

    if request.content_type == "application/json":
        return web.json_response({"code": share_code})
    else:
        raise web.HTTPSeeOther("/share/" + share_code)


@route("/{share_code}/{track_code}/cover", public=True)
async def cover(request: web.Request, conn: Connection):
    """
    Route providing a WEBP album cover image
    """
    track = track_from_url(conn, request)
    cover_bytes = await track.get_cover(meme=False, img_quality=ImageQuality.HIGH, img_format=ImageFormat.WEBP)
    return web.Response(body=cover_bytes, content_type="image/webp")


@route("/{share_code}/{track_code}/audio", public=True)
async def audio(request: web.Request, conn: Connection):
    """
    Route to stream opus audio.
    """
    track = track_from_url(conn, request)
    return await blob.AudioBlob(track, AudioFormat.WEBM_OPUS_HIGH).response()


@route("/{share_code}/{track_code}/download/{file_format}", public=True)
async def download(request: web.Request, conn: Connection):
    """
    Route to download an audio file.
    """
    track = track_from_url(conn, request)

    file_format = request.match_info["file_format"]
    if file_format == "original":
        response = web.FileResponse(track.filepath)
        response.headers["Content-Disposition"] = f'attachment; filename="{track.filename}"'
    elif file_format == "mp3":
        response = await blob.AudioBlob(track, AudioFormat.MP3_WITH_METADATA).response()
        download_name = track.download_name() + ".mp3"
        response.headers["Content-Disposition"] = f'attachment; filename="{download_name}"'
    else:
        raise web.HTTPBadRequest(reason="invalid format")

    return response


@route("/{share_code}", public=True)
async def show_share(request: web.Request, conn: Connection):
    """
    Web page displaying a share.
    """
    share_code = request.match_info["share_code"]
    tracks: list[tuple[str, str]] = []
    for track_code, relpath in conn.execute(
        "SELECT track_code, track FROM share_track WHERE share_code = ?", (share_code,)
    ).fetchall():
        display = FileTrack(conn, relpath).display_title()
        tracks.append((track_code, display))

    if len(tracks) == 1:
        track_code, _relpath = tracks[0]
        raise web.HTTPSeeOther("/share/" + share_code + "/" + track_code)

    (shared_by,) = conn.execute(
        """
        SELECT COALESCE(nickname, username)
        FROM share JOIN user ON share.user = user.id
        WHERE share_code=?
        """,
        (share_code,),
    ).fetchone()

    return await template("share.jinja2", share_code=share_code, shared_by=shared_by, tracks=tracks)


@route("/{share_code}/json", public=True)
async def show_share_json(request: web.Request, conn: Connection):
    """
    Return list of tracks belonging to this share, in json format
    """
    share_code = request.match_info["share_code"]
    tracks = [row[0] for row in conn.execute("SELECT track_code FROM share_track WHERE share_code = ?", (share_code,))]
    return web.json_response(tracks)


@route("/{share_code}/{track_code}", public=True)
async def show_single(request: web.Request, conn: Connection):
    """
    Web page displaying a single shared track.
    """
    track = track_from_url(conn, request)

    share_code = request.match_info["share_code"]
    track_code = request.match_info["track_code"]

    share_track_count = conn.execute("SELECT COUNT(*) FROM share_track WHERE share_code = ?", (share_code,)).fetchone()[
        0
    ]
    lyrics = ensure_plain(track.parsed_lyrics)
    lyrics_text = lyrics.text if lyrics else None

    return await template(
        "share_single.jinja2",
        share_code=share_code,
        track_code=track_code,
        track=track.display_title(),
        lyrics=lyrics_text,
        share_track_count=share_track_count,
    )
