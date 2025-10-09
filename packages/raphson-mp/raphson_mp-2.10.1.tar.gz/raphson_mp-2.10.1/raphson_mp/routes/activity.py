from datetime import datetime
import logging
import time
from sqlite3 import Connection
from typing import TypedDict, cast

from aiohttp import web

from raphson_mp.common.track import VIRTUAL_PLAYLIST, NoSuchTrackError, relpath_playlist
from raphson_mp.server import activity, i18n
from raphson_mp.server.auth import PrivacyOption, User
from raphson_mp.server.decorators import route
from raphson_mp.server.response import template
from raphson_mp.server.track import FileTrack

log = logging.getLogger(__name__)


def _action_translation(action: str):
    if action == "insert":
        return i18n.gettext("Added")
    elif action == "delete":
        return i18n.gettext("Removed")
    elif action == "update":
        return i18n.gettext("Modified")
    elif action == "move":
        return i18n.gettext("Moved")
    else:
        raise ValueError(action)


@route("", redirect_to_login=True)
async def route_activity(_request: web.Request, conn: Connection, _user: User):
    """
    Main activity page, showing currently playing tracks and history of
    played tracks and modified files.
    """
    initial_play_data: list[tuple[int, str, str, str]] = []

    for timestamp, relpath, username in conn.execute(
        """
        SELECT timestamp, track, COALESCE(nickname, username)
        FROM history
            LEFT JOIN user ON history.user = user.id
        WHERE history.private = 0
        ORDER BY history.timestamp DESC
        LIMIT 10
        """
    ).fetchall():
        try:
            track = FileTrack(conn, relpath)
        except NoSuchTrackError:
            continue
        initial_play_data.append((timestamp, username, track.playlist, track.display_title()))

    initial_file_data: list[tuple[int, str, str, str]] = [
        (timestamp, username, _action_translation(action), track)
        for timestamp, action, track, username in conn.execute(
            f"""
            SELECT timestamp, action, track, COALESCE(nickname, username, '')
            FROM scanner_log LEFT JOIN user ON user = user.id
            ORDER BY timestamp DESC
            LIMIT 10
            """
        )
    ]

    return await template("activity.jinja2", initial_play_data=initial_play_data, initial_file_data=initial_file_data)


class FileChange(TypedDict):
    timestamp: int
    time_ago: str
    username: str
    action: str
    playlist: str
    track: str


@route("/files")
async def route_files(_request: web.Request, conn: Connection, _user: User):
    """
    Page with long static list of changed files history, similar to route_all()
    """
    result = conn.execute(
        f"""
        SELECT timestamp, action, playlist, track, COALESCE(nickname, username, '')
        FROM scanner_log LEFT JOIN user ON user = user.id
        ORDER BY timestamp DESC
        LIMIT 1000
        """
    )

    changes: list[FileChange] = [
        {
            "timestamp": timestamp,
            "time_ago": i18n.format_timedelta(timestamp - int(time.time()), add_direction=True, granularity="minute"),
            "username": username,
            "action": _action_translation(action),
            "playlist": playlist,
            "track": track,
        }
        for timestamp, action, playlist, track, username in result
    ]

    return await template("activity_files.jinja2", changes=changes)


class HistoryItem(TypedDict):
    time: int
    username: str
    playlist: str
    title: str


@route("/all")
async def route_all(_request: web.Request, conn: Connection, _user: User):
    """
    Page with long static list of playback history, similar to route_files()
    """
    result = conn.execute(
        """
        SELECT history.timestamp, COALESCE(nickname, username, ''), history.playlist, history.track, track.path IS NOT NULL
        FROM history
            LEFT JOIN user ON history.user = user.id
            LEFT JOIN track ON history.track = track.path
        ORDER BY history.timestamp DESC
        LIMIT 1000
        """
    )
    history: list[HistoryItem] = []
    for timestamp, username, playlist, relpath, track_exists in result:
        if track_exists:
            title = FileTrack(conn, relpath).display_title()
        else:
            title = relpath

        history.append({"time": timestamp, "username": username, "playlist": playlist, "title": title})

    return await template("activity_all.jinja2", history=history)


@route("/played", method="POST")
async def route_played(request: web.Request, conn: Connection, user: User):
    """
    Route to submit an entry to played tracks history, optionally also
    scrobbling to last.fm. Used by web music player and also by offline
    sync to submit many previously played tracks.
    POST body:
     - track: relpath
     - timestamp: time at which track met played conditions (roughly)
     - csrf: csrf token (ignored in offline mode)
    """
    if user.privacy == PrivacyOption.HIDDEN:
        log.info("ignoring because privacy==hidden")
        raise web.HTTPNoContent()

    json = await request.json()
    relpath = cast(str, json["track"])
    playlist = relpath_playlist(relpath)
    if playlist is VIRTUAL_PLAYLIST:
        log.debug('ignore played for virtual track')
        raise web.HTTPNoContent()

    if "timestamp" in json:
        timestamp = int(cast(str, json["timestamp"]))
        if timestamp - time.time() > 3600:
            log.warning('ignoring played with time more than an hour into the future: %s from user: %s', datetime.fromtimestamp(timestamp).isoformat(), user.username)
            raise web.HTTPNoContent()
    else:
        timestamp = int(time.time())

    try:
        track = FileTrack(conn, relpath)
        await activity.set_played(conn, user, track, timestamp)
    except NoSuchTrackError:
        log.warning("skipping track that does not exist: %s", relpath)

    raise web.HTTPNoContent()


@route("/stop", method="POST")
async def route_stop(request: web.Request, _conn: Connection, user: User):
    player_id = cast(str, (await request.post())["id"])
    await activity.stop_playing(user, player_id)
    raise web.HTTPNoContent()
