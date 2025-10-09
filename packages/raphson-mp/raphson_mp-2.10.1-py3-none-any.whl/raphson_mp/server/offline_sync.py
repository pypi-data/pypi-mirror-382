import asyncio
import json
import logging
import random
import time
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from typing_extensions import override

from raphson_mp.client import RaphsonMusicClient
from raphson_mp.client.track import Track
from raphson_mp.common import httpclient, util
from raphson_mp.server import db

_LOGGER = logging.getLogger(__name__)
_SYNC_PARALLEL = 3  # sync 3 tracks simultaneously


class SyncProgress(ABC):
    @abstractmethod
    def task_start(self, task: str): ...

    @abstractmethod
    def task_done(self, task: str): ...

    @abstractmethod
    def task_error(self, task: str): ...

    @abstractmethod
    def all_done(self): ...


class CommandLineSyncProgress(SyncProgress):
    start_time: dict[str, int] = {}

    @override
    def task_start(self, task: str):
        self.start_time[task] = time.time_ns()
        _LOGGER.info("start: %s", task)

    @override
    def task_done(self, task: str):
        duration = (time.time_ns() - self.start_time[task]) // 1_000_000
        del self.start_time[task]
        _LOGGER.info("done: %s (%sms)", task, duration)

    @override
    def task_error(self, task: str):
        del self.start_time[task]
        _LOGGER.warning("error: %s", task, exc_info=True)

    @override
    def all_done(self):
        _LOGGER.info("all done")
        pass


class WebResponseProgress(CommandLineSyncProgress):
    queue: asyncio.Queue[str | None]

    def __init__(self):
        self.queue = asyncio.Queue()

    @override
    def task_start(self, task: str):
        super().task_start(task)
        self.queue.put_nowait(json.dumps({"task": task, "state": "start"}) + "\n")

    @override
    def task_done(self, task: str):
        super().task_done(task)
        self.queue.put_nowait(json.dumps({"task": task, "state": "done"}) + "\n")

    @override
    def task_error(self, task: str):
        super().task_error(task)
        self.queue.put_nowait(json.dumps({"task": task, "state": "error"}) + "\n")

    @override
    def all_done(self):
        super().all_done()
        self.queue.put_nowait(json.dumps({"state": "all_done"}) + "\n")
        # TODO use queue.shutdown() when upgraded to Python 3.12
        self.queue.put_nowait(None)

    async def response_bytes(self) -> AsyncIterator[bytes]:
        while True:
            entry = await self.queue.get()
            if entry:
                yield entry.encode()
            else:
                break


class SyncError(Exception):
    pass


class OfflineSync:
    progress: SyncProgress
    client: RaphsonMusicClient
    stop_event: asyncio.Event
    force_resync: float
    track_semaphore: asyncio.Semaphore

    def __init__(self, progress: SyncProgress, force_resync: float):
        self.progress = progress
        self.client = RaphsonMusicClient()
        self.stop_event = asyncio.Event()
        self.force_resync = force_resync
        self.track_semaphore = asyncio.Semaphore(_SYNC_PARALLEL)

    async def setup(self):
        with db.OFFLINE.connect() as offline:
            row = offline.execute("SELECT base_url, token FROM settings").fetchone()
            if row:
                base_url, token = row
            else:
                raise SyncError("Sync server not configured")

        await self.client.setup(base_url=base_url, user_agent=httpclient.USER_AGENT, token=token)

    async def _download_track_content(self, track: Track) -> None:
        """
        Download audio and album cover for a track and store in the 'content' database table.
        """
        download = await track.download(self.client)

        with db.OFFLINE.connect() as offline:
            offline.execute(
                """
                INSERT INTO content (path, music_data, cover_data, lyrics_json)
                VALUES (:path, :music_data, :cover_data, :lyrics_json)
                ON CONFLICT (path) DO UPDATE SET
                    music_data = :music_data, cover_data = :cover_data, lyrics_json = :lyrics_json
                """,
                {
                    "path": track.path,
                    "music_data": download.audio,
                    "cover_data": download.image,
                    "lyrics_json": "{}",
                },
            )

    async def _update_track(self, track: Track) -> None:
        await self._download_track_content(track)

        with db.MUSIC.connect() as conn:
            conn.execute(
                "UPDATE track SET duration=?, title=?, album=?, album_artist=?, year=?, mtime=?, ctime=?, lyrics=? WHERE path=?",
                (
                    track.duration,
                    track.title,
                    track.album,
                    track.album_artist,
                    track.year,
                    track.mtime,
                    track.ctime,
                    track.lyrics,
                    track.path,
                ),
            )
            conn.execute("DELETE FROM track_artist WHERE track=?", (track.path,))
            conn.executemany(
                "INSERT INTO track_artist (track, artist) VALUES (?, ?)",
                [(track.path, artist) for artist in track.artists],
            )
            conn.execute("DELETE FROM track_tag WHERE track=?", (track.path,))
            conn.executemany(
                "INSERT INTO track_tag (track, tag) VALUES (?, ?)",
                [(track.path, tag) for tag in track.tags],
            )

    async def _insert_track(
        self,
        playlist: str,
        track: Track,
    ) -> None:
        await self._download_track_content(track)

        with db.MUSIC.connect() as conn:
            conn.execute(
                """
                INSERT INTO track (path, playlist, duration, title, album, album_artist, year, mtime, ctime, lyrics)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    track.path,
                    playlist,
                    track.duration,
                    track.title,
                    track.album,
                    track.album_artist,
                    track.year,
                    track.mtime,
                    track.ctime,
                    track.lyrics,
                ),
            )
            conn.executemany(
                "INSERT INTO track_artist (track, artist) VALUES (?, ?)",
                [(track.path, artist) for artist in track.artists],
            )
            conn.executemany(
                "INSERT INTO track_tag (track, tag) VALUES (?, ?)",
                [(track.path, tag) for tag in track.tags],
            )

    async def _prune_tracks(self, track_paths: set[str]):
        with db.MUSIC.connect() as conn, db.OFFLINE.connect() as offline:
            rows = conn.execute("SELECT path FROM track").fetchall()
            for (path,) in rows:
                if path not in track_paths:
                    self.progress.task_start("Delete: " + path)
                    conn.execute("DELETE FROM track WHERE path=?", (path,))
                    offline.execute("DELETE FROM content WHERE path=?", (path,))
                    self.progress.task_done("Delete: " + path)
                    await asyncio.sleep(0)

    async def _prune_playlists(self):
        # Remove empty playlists
        self.progress.task_start("Remove empty playlists")

        with db.MUSIC.connect() as conn:
            rows = conn.execute(
                """
                SELECT name
                FROM playlist
                WHERE (SELECT COUNT(*) FROM track WHERE track.playlist=playlist.name) = 0
                """
            ).fetchall()

            for (name,) in rows:
                _LOGGER.info("Delete empty playlist: %s", name)
                conn.execute("DELETE FROM playlist WHERE name=?", (name,))
                await asyncio.sleep(0)

        self.progress.task_done("Remove empty playlists")

    async def _sync_tracks_for_playlist(
        self,
        playlist: str,
        dislikes: set[str],
        all_track_paths: set[str],
    ) -> None:
        with db.MUSIC.connect() as conn:
            if not conn.execute("SELECT 1 FROM playlist WHERE name = ?", (playlist,)).fetchone():
                self.progress.task_start("Create playlist: " + playlist)
                conn.execute("INSERT INTO playlist VALUES (?)", (playlist,))
                self.progress.task_done("Create playlist: " + playlist)

        self.progress.task_start("Fetch track list: " + playlist)
        tracks = await self.client.list_tracks(playlist)
        self.progress.task_done("Fetch track list: " + playlist)

        for track in tracks:
            if track.path in dislikes:
                continue

            all_track_paths.add(track.path)

            async def sync_task(track: Track):
                with db.MUSIC.connect() as conn:
                    task_name: str | None = None
                    try:
                        row = conn.execute("SELECT mtime FROM track WHERE path=?", (track.path,)).fetchone()
                        if row:
                            (mtime,) = row
                            if mtime != track.mtime:
                                task_name = "Update: " + track.path
                                self.progress.task_start(task_name)
                                await self._update_track(track)
                            elif self.force_resync > 0 and random.random() < self.force_resync:
                                task_name = "Force update: " + track.path
                                self.progress.task_start(task_name)
                                await self._update_track(track)
                        else:
                            task_name = "Download missing: " + track.path
                            self.progress.task_start(task_name)
                            await self._insert_track(playlist, track)
                        if task_name:
                            self.progress.task_done(task_name)
                    except Exception as ex:
                        if isinstance(ex, asyncio.CancelledError):
                            pass
                        if task_name:
                            self.progress.task_error(task_name)
                    finally:
                        self.track_semaphore.release()

            await self.track_semaphore.acquire()
            util.create_task(sync_task(track))

    async def get_dislikes(self) -> set[str]:
        self.progress.task_start("Fetch dislikes")
        dislikes = await self.client.dislikes()
        self.progress.task_done("Fetch dislikes")
        return dislikes

    async def sync_tracks(self) -> None:
        """
        Download added or modified tracks from the server, and delete local tracks that were deleted on the server
        """
        with db.OFFLINE.connect() as offline:
            result = offline.execute("SELECT name FROM playlists")
            enabled_playlists = [row[0] for row in result]

        if len(enabled_playlists) == 0:
            self.progress.task_start("Fetch favorite playlists")
            playlists = await self.client.playlists()
            enabled_playlists = [playlist.name for playlist in playlists if playlist.favorite]
            self.progress.task_done("Fetch favorite playlists")

        dislikes = await self.get_dislikes()

        all_track_paths: set[str] = set()

        for playlist in enabled_playlists:
            await self._sync_tracks_for_playlist(playlist, dislikes, all_track_paths)

        await util.await_tasks()

        await self._prune_tracks(all_track_paths)
        await self._prune_playlists()

    async def sync_history(self):
        """
        Send local playback history to server
        """

        with db.OFFLINE.connect() as offline:
            rows = offline.execute("SELECT rowid, timestamp, track FROM history ORDER BY timestamp ASC").fetchall()

            for rowid, timestamp, track in rows:
                self.progress.task_start("Submit played: " + track)
                await self.client.submit_played(track, timestamp)
                offline.execute("DELETE FROM history WHERE rowid=?", (rowid,))
                self.progress.task_done("Submit played: " + track)

    async def run(self) -> None:
        try:
            await self.setup()
            await self.sync_history()
            await self.sync_tracks()
        except Exception:
            _LOGGER.error("Unhandled exception", exc_info=True)
        finally:
            self.progress.all_done()
            if self.client:
                await self.client.close()

    def stop(self) -> None:
        if not self.stop_event.is_set():
            self.progress.task_start("stop")
            self.stop_event.set()


async def change_playlists(playlists: list[str]) -> None:
    if len(playlists) == 0:
        _LOGGER.info("Resetting enabled playlists")
    else:
        _LOGGER.info("Changing playlists: %s", ",".join(playlists))

    with db.OFFLINE.connect() as conn:
        conn.execute("BEGIN")
        conn.execute("DELETE FROM playlists")
        conn.executemany("INSERT INTO playlists VALUES (?)", [(playlist,) for playlist in playlists])
        conn.execute("COMMIT")


def change_settings(server: str, token: str):
    with db.OFFLINE.connect() as conn:
        if conn.execute("SELECT base_url FROM settings").fetchone():
            conn.execute("UPDATE settings SET base_url=?, token=?", (server, token))
        else:
            conn.execute("INSERT INTO settings (base_url, token) VALUES (?, ?)", (server, token))
