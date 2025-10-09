import dataclasses
import logging
from sqlite3 import Connection
from typing import Any

from aiohttp import web

from raphson_mp.common.image import ImageFormat, ImageQuality
from raphson_mp.common.track import (
    AudioFormat,
    NoSuchTrackError,
    VirtualTrackUnavailableError,
    relpath_playlist,
)
from raphson_mp.server import acoustid, blob, musicbrainz, scanner
from raphson_mp.server.auth import User
from raphson_mp.server.blob import VideoBlob
from raphson_mp.server.decorators import route
from raphson_mp.server.playlist import Playlist
from raphson_mp.server.track import FileTrack, Track, get_track
from raphson_mp.server.virtual_track import VirtualTrack

log = logging.getLogger(__name__)


async def _track(conn: Connection, relpath: str) -> Track:
    try:
        track = await get_track(conn, relpath)
    except NoSuchTrackError:
        raise web.HTTPNotFound(reason="track not found")
    except VirtualTrackUnavailableError:
        raise web.HTTPServiceUnavailable()
    return track


@route("/{relpath}/info")
async def route_info(request: web.Request, conn: Connection, _user: User):
    relpath = request.match_info["relpath"]
    track = await _track(conn, relpath)
    return web.json_response(track.to_dict())


@route("/{relpath}/video")
async def route_video(request: web.Request, conn: Connection, _user: User):
    """
    Return video stream
    """
    relpath = request.match_info["relpath"]
    track = await _track(conn, relpath)
    if not isinstance(track, FileTrack):
        raise web.HTTPBadRequest(reason="video not available for virtual tracks")
    if not track.video:
        raise web.HTTPBadRequest(reason="video not available for this track")
    blob = VideoBlob(track)
    return await blob.response()


@route("/{relpath}/audio")
async def route_audio(request: web.Request, conn: Connection, _user: User):
    """
    Get transcoded audio for the given track path.
    """
    relpath = request.match_info["relpath"]
    track = await _track(conn, relpath)

    audio_format = AudioFormat(request.query.get("type", AudioFormat.WEBM_OPUS_HIGH.value))

    if isinstance(track, FileTrack):
        response = await blob.AudioBlob(track, audio_format).response()
    elif isinstance(track, VirtualTrack):
        response = await track.get_audio(audio_format)
    else:
        raise ValueError(track)

    if audio_format is AudioFormat.MP3_WITH_METADATA:
        mp3_name = track.download_name()
        response.headers["Content-Disposition"] = f'attachment; filename="{mp3_name}"'

    if "mtime" in request.query:  # if cache busting mtime is present, we can serve with a long cache time
        response.headers["Cache-Control"] = "immutable, max-age=604800"
    return response


@route("/{relpath}/cover")
async def route_album_cover(request: web.Request, conn: Connection, _user: User):
    """
    Get album cover image for the provided track path.
    """
    relpath = request.match_info["relpath"]
    track = await _track(conn, relpath)

    quality = ImageQuality(request.query.get("quality", ImageQuality.HIGH))
    format = ImageFormat(request.query.get("format", ImageFormat.WEBP))
    meme = bool(int(request.query.get("meme", "0")))

    image_bytes = await track.get_cover(meme, quality, format)

    response = web.Response(body=image_bytes, content_type=format.content_type)
    if "mtime" in request.query:  # if cache busting mtime is present, we can serve with a long cache time
        response.headers["Cache-Control"] = "immutable, max-age=604800"
    return response


@route("/{relpath}/update_metadata", method="POST")
async def route_update_metadata(request: web.Request, conn: Connection, user: User):
    """
    Endpoint to update track metadata
    """
    relpath = request.match_info["relpath"]
    track = await _track(conn, relpath)
    assert isinstance(track, FileTrack)

    playlist = Playlist(conn, relpath_playlist(relpath), user)
    if not playlist.is_writable:
        raise web.HTTPForbidden(reason="No write permission for this playlist")

    json = await request.json()
    track.title = json["title"]
    track.album = json["album"]
    track.artists = json["artists"]
    track.album_artist = json["album_artist"]
    track.tags = json["tags"]
    track.year = json["year"]
    track.track_number = json["track_number"]
    track.lyrics = json["lyrics"]

    await track.save()

    await scanner.scan_track(user, track.filepath)

    raise web.HTTPNoContent()


@route("/{relpath}/acoustid")
async def route_acoustid(request: web.Request, conn: Connection, _user: User):
    relpath = request.match_info["relpath"]
    track = await _track(conn, relpath)
    assert isinstance(track, FileTrack)
    fp = await acoustid.get_fingerprint(track.filepath)

    for result in await acoustid.lookup(fp):
        for recording in result["recordings"]:
            log.info("found track=%s recording=%s", result["id"], recording["id"])

            meta_list: list[dict[str, Any]] = []
            known_ids: set[str] = set()
            async for meta in musicbrainz.get_recording_metadata(recording["id"]):
                if meta.id in known_ids:
                    continue
                log.info("found possible metadata: %s", meta)
                meta_list.append(dataclasses.asdict(meta))
                known_ids.add(meta.id)

            return web.json_response(
                {
                    "acoustid": result["id"],
                    "releases": meta_list,
                }
            )

    raise web.HTTPNoContent()


@route("/{relpath}/report_problem", method="POST")
async def report_problem(request: web.Request, conn: Connection, _user: User):
    relpath = request.match_info["relpath"]
    conn.execute("INSERT OR IGNORE INTO track_problem VALUES (?)", (relpath,))
    raise web.HTTPNoContent()
