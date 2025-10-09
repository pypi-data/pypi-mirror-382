from __future__ import annotations

import asyncio
import logging
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from sqlite3 import Connection

from raphson_mp.common import eventbus, util
from raphson_mp.common.control import FileAction
from raphson_mp.common.track import VIRTUAL_PLAYLIST, relpath_playlist
from raphson_mp.server import auth, db, events, ffmpeg, settings, track
from raphson_mp.server.playlist import Playlist

log = logging.getLogger(__name__)

SCANNER_LOCK = threading.Lock()


class Counter:
    count: int = 0


def _scan_playlists(conn: Connection) -> set[str]:
    """
    Scan playlist directories, add or remove playlists from the database
    where necessary.
    """
    assert settings.music_dir is not None
    names_db = {row[0] for row in conn.execute("SELECT name FROM playlist")}
    paths_disk = [path for path in settings.music_dir.iterdir() if path.is_dir() and not track.is_trashed(path)]
    names_disk = {path.name for path in paths_disk}

    add_to_db: list[tuple[str]] = []
    remove_from_db: list[tuple[str]] = []

    for name in names_db:
        if name not in names_disk:
            log.info("going to delete playlist: %s", name)
            remove_from_db.append((name,))

    for name in names_disk:
        if name not in names_db:
            log.info("new playlist: %s", name)
            add_to_db.append((name,))

    if add_to_db:
        conn.executemany("INSERT INTO playlist (name) VALUES (?)", add_to_db)
    if remove_from_db:
        conn.executemany("DELETE FROM playlist WHERE name=?", remove_from_db)

    return names_disk


async def scan_playlists():
    def thread():
        with SCANNER_LOCK:
            with db.MUSIC.connect() as conn:
                _scan_playlists(conn)

    await asyncio.to_thread(thread)


def _update_db(
    loop: asyncio.AbstractEventLoop,
    conn: Connection,
    user: auth.User | None,
    path: Path,
    relpath: str,
    mtime: int,
    update: bool,
) -> bool:
    meta = asyncio.run_coroutine_threadsafe(ffmpeg.probe_metadata(path), loop).result()
    if meta is None:
        if update:
            log.warning("Metadata error, delete track from database")
            conn.execute("DELETE FROM track WHERE path=?", (relpath,))
            _log(loop, conn, events.FileChangeEvent(FileAction.DELETE, relpath, user))
        return False

    playlist = relpath_playlist(relpath)
    assert playlist != VIRTUAL_PLAYLIST
    ctime = int(time.time())

    conn.execute("BEGIN")

    if update:
        conn.execute(
            """
            UPDATE track
            SET duration=?, title=?, album=?, album_artist=?, track_number=?, year=?, lyrics=?, video=?, mtime=?
            WHERE path=?
            """,
            (
                meta.duration,
                meta.title,
                meta.album,
                meta.album_artist,
                meta.track_number,
                meta.year,
                meta.lyrics,
                meta.video,
                mtime,
                relpath,
            ),
        )
    else:
        conn.execute(
            """
            INSERT INTO track (path, playlist, duration, title, album, album_artist, track_number, year, lyrics, video, mtime, ctime)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                relpath,
                playlist,
                meta.duration,
                meta.title,
                meta.album,
                meta.album_artist,
                meta.track_number,
                meta.year,
                meta.lyrics,
                meta.video,
                mtime,
                ctime,
            ),
        )

    if update:
        conn.execute("DELETE FROM track_artist WHERE track=?", (relpath,))
        conn.execute("DELETE FROM track_tag WHERE track=?", (relpath,))

    conn.executemany(
        "INSERT INTO track_artist (track, artist) VALUES (?, ?)", [(relpath, artist) for artist in meta.artists]
    )
    conn.executemany("INSERT INTO track_tag (track, tag) VALUES (?, ?)", [(relpath, tag) for tag in meta.tags])

    conn.execute("COMMIT")

    if update:
        _log(loop, conn, events.FileChangeEvent(FileAction.UPDATE, relpath, user))
    else:
        _log(loop, conn, events.FileChangeEvent(FileAction.INSERT, relpath, user))

    return True


def _scan_track(
    loop: asyncio.AbstractEventLoop,
    conn: Connection,
    user: auth.User | None,
    path: Path,
    relpath: str,
) -> bool:
    """
    Scan single track.
    Returns: Whether track exists (False if deleted)
    """
    if not track.is_music_file(path):
        if conn.execute("SELECT 1 FROM track WHERE path = ?", (relpath,)).fetchone() is None:
            # track already doesn't exist
            return False

        log.info("deleted: %s", relpath)
        conn.execute("DELETE FROM track WHERE path=?", (relpath,))
        _log(loop, conn, events.FileChangeEvent(FileAction.DELETE, relpath, user))
        return False

    row = conn.execute("SELECT mtime FROM track WHERE path=?", (relpath,)).fetchone()
    db_mtime = row[0] if row else None
    file_mtime = int(path.stat().st_mtime)

    if db_mtime is None:
        # Track does not yet exist in database
        log.info("new track, insert: %s", relpath)
        return _update_db(loop, conn, user, path, relpath, file_mtime, False)

    if file_mtime != db_mtime:
        # Update existing track in database
        log.info(
            "Changed, update: %s (%s to %s)",
            relpath,
            datetime.fromtimestamp(db_mtime, tz=timezone.utc),
            datetime.fromtimestamp(file_mtime, tz=timezone.utc),
        )
        return _update_db(loop, conn, user, path, relpath, file_mtime, True)

    # Track exists in filesystem and is unchanged
    return True


def _scan_playlist(
    loop: asyncio.AbstractEventLoop,
    conn: Connection,
    user: auth.User | None,
    playlist: str,
    counter: Counter | None,
) -> None:
    """
    Scan for added, removed or changed tracks in a playlist.
    """
    assert playlist # ensure playlist name is not empty
    log.info("scanning playlist: %s", playlist)
    paths_db: set[str] = set()
    with util.log_duration("scan existing tracks"):
        for (track_relpath,) in conn.execute("SELECT path FROM track WHERE playlist=?", (playlist,)).fetchall():
            if counter:
                counter.count += 1
            if _scan_track(loop, conn, user, track.from_relpath(track_relpath), track_relpath):
                paths_db.add(track_relpath)

    with util.log_duration("scan new tracks"):
        for track_path in track.list_tracks_recursively(track.from_relpath(playlist)):
            track_relpath = track.to_relpath(track_path)
            if track_relpath not in paths_db:
                if counter:
                    counter.count += 1
                _scan_track(loop, conn, user, track_path, track_relpath)


async def scan_playlist(user: auth.User | None, playlist: str | Playlist) -> None:
    """
    Scan for added, removed or changed tracks in a playlist.
    Returns: number of changes
    """
    loop = asyncio.get_running_loop()

    def thread():
        with SCANNER_LOCK:
            with db.MUSIC.connect() as conn:
                _scan_playlist(loop, conn, user, playlist.name if isinstance(playlist, Playlist) else playlist, None)

    await asyncio.to_thread(thread)


async def scan_track(user: auth.User | None, path: Path) -> None:
    """
    Scan single track for changes
    """
    loop = asyncio.get_running_loop()

    def thread():
        relpath = track.to_relpath(path)
        with SCANNER_LOCK:
            with db.MUSIC.connect() as conn:
                _scan_track(loop, conn, user, path, relpath)

    await asyncio.to_thread(thread)


async def move(user: auth.User | None, from_path: Path, to_path: Path):
    loop = asyncio.get_running_loop()

    def thread():
        from_relpath = track.to_relpath(from_path)
        to_relpath = track.to_relpath(to_path)
        to_playlist = relpath_playlist(to_relpath)
        was_music_file = track.is_music_file(from_path)
        from_path.rename(to_path)
        now_music_file = track.is_music_file(to_path)
        with db.MUSIC.connect() as conn:
            # The file was renamed to add or remove a music extension, or trashed. It should be scanned to add or remove the track.
            if was_music_file != now_music_file:
                with SCANNER_LOCK:
                    _scan_track(loop, conn, user, from_path, from_relpath)
                    _scan_track(loop, conn, user, to_path, to_relpath)
                    return

            try:
                if to_path.is_dir():
                    # need to update all children of this directory
                    conn.execute("BEGIN")
                    for (change_relpath,) in conn.execute(
                        "SELECT path FROM track WHERE path LIKE ?", (from_relpath + "/%",)
                    ).fetchall():
                        new_relpath = to_relpath + change_relpath[len(from_relpath) :]
                        log.debug("track in directory has moved from %s to %s", change_relpath, new_relpath)
                        conn.execute(
                            "UPDATE track SET path = ?, playlist = ? WHERE path = ?",
                            (new_relpath, to_playlist, change_relpath),
                        )
                        _log(loop, conn, events.FileChangeEvent(FileAction.MOVE, new_relpath, user))
                    conn.execute("COMMIT")
                    return

                # the file might not be in the db, if it's not a music file or if it hasn't been scanned yet
                in_db = conn.execute("SELECT 1 FROM track WHERE path = ?", (from_relpath,)).fetchone() is not None
                if in_db:
                    conn.execute(
                        "UPDATE track SET path = ?, playlist = ? WHERE path = ?",
                        (to_relpath, to_playlist, from_relpath),
                    )
                    _log(loop, conn, events.FileChangeEvent(FileAction.MOVE, to_relpath, user))
            except Exception as ex:
                # if this somehow went wrong, attempt to rename the track back before raising the exception again
                to_path.rename(from_path)
                raise ex

    await asyncio.to_thread(thread)


def last_change(conn: Connection, playlist: str | None) -> datetime:
    if settings.offline_mode:
        return datetime.now(tz=timezone.utc)

    if playlist is not None:
        query = "SELECT MAX(timestamp) FROM scanner_log WHERE playlist = ?"
        params = (playlist,)
    else:
        query = "SELECT MAX(timestamp) FROM scanner_log"
        params = ()
    (mtime,) = conn.execute(query, params).fetchone()
    if mtime is None:
        mtime = 0

    return datetime.fromtimestamp(mtime, timezone.utc)


async def scan(user: auth.User | None, counter: Counter | None = None) -> None:
    """
    Main function for scanning music directory structure
    """
    if settings.offline_mode:
        log.info("skip scanner in offline mode")
        return

    loop = asyncio.get_running_loop()

    def thread():
        with SCANNER_LOCK:
            with db.MUSIC.connect() as conn:
                playlists = _scan_playlists(conn)
                for playlist in playlists:
                    _scan_playlist(loop, conn, user, playlist, counter)

    await asyncio.to_thread(thread)


def _log(loop: asyncio.AbstractEventLoop, conn: Connection, event: events.FileChangeEvent):
    asyncio.run_coroutine_threadsafe(eventbus.fire(event), loop)
    playlist_name = event.track[: event.track.index("/")]
    user_id = event.user.user_id if event.user else None

    conn.execute(
        """
        INSERT INTO scanner_log (timestamp, action, playlist, track, user)
        VALUES (?, ?, ?, ?, ?)
        """,
        (int(time.time()), event.action.value, playlist_name, event.track, user_id),
    )
