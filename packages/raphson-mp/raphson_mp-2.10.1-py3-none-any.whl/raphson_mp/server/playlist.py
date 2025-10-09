import asyncio
import logging
import time
from pathlib import Path
from sqlite3 import Connection
from typing_extensions import override

from aiohttp import web

from raphson_mp.common.playlist import PlaylistBase
from raphson_mp.common.tag import TagMode
from raphson_mp.common.track import VIRTUAL_PLAYLIST, relpath_playlist
from raphson_mp.server import auth, settings
from raphson_mp.server.track import FileTrack, Track, from_relpath, to_relpath

_LOGGER = logging.getLogger(__name__)
_TRACK_CHOOSE_LOCK = asyncio.Lock()


class PlaylistStats:
    name: str
    track_count: int
    total_duration: int
    mean_duration: int
    artist_count: int
    has_title_count: int
    has_album_count: int
    has_album_artist_count: int
    has_year_count: int
    has_artist_count: int
    has_tag_count: int
    most_recent_choice: int
    least_recent_choice: int
    most_recent_mtime: int

    def __init__(self, conn: Connection, name: str):
        self.name = name
        row = conn.execute(
            "SELECT COUNT(*), SUM(duration), AVG(duration) FROM track WHERE playlist=?",
            (name,),
        ).fetchone()
        self.track_count, self.total_duration, self.mean_duration = row

        row = conn.execute(
            """
            SELECT COUNT(DISTINCT artist)
            FROM track_artist JOIN track ON track.path=track
            WHERE playlist=?
            """,
            (name,),
        ).fetchone()
        (self.artist_count,) = row

        (
            self.has_title_count,
            self.has_album_count,
            self.has_album_artist_count,
            self.has_year_count,
            self.most_recent_choice,
            self.least_recent_choice,
            self.most_recent_mtime,
        ) = conn.execute(
            """
            SELECT SUM(title IS NOT NULL),
                    SUM(album IS NOT NULL),
                    SUM(album_artist IS NOT NULL),
                    SUM(year IS NOT NULL),
                    MAX(last_chosen),
                    MIN(last_chosen),
                    MAX(mtime)
            FROM track WHERE playlist=?
            """,
            (name,),
        ).fetchone()

        (self.has_artist_count,) = conn.execute(
            """
            SELECT COUNT(DISTINCT track)
            FROM track_artist JOIN track ON track.path = track
            WHERE playlist=?
            """,
            (name,),
        ).fetchone()

        (self.has_tag_count,) = conn.execute(
            """
            SELECT COUNT(DISTINCT track)
            FROM track_tag JOIN track ON track.path = track
            WHERE playlist=?
            """,
            (name,),
        ).fetchone()


class Playlist(PlaylistBase):
    duration: int
    _is_primary: bool | None = None
    _is_writable: bool | None = None
    _is_favorite: bool | None = None

    def __init__(self, conn: Connection, name: str, user: auth.User | None = None):
        if name == VIRTUAL_PLAYLIST:
            raise ValueError("cannot create Playlist object for virtual playlist")

        track_count, self.duration = conn.execute(
            "SELECT COUNT(*), COALESCE(SUM(duration), 0) FROM track WHERE playlist=?", (name,)
        ).fetchone()

        super().__init__(name=name, track_count=track_count)

        if user is not None:
            self._is_primary = name == user.primary_playlist

            if user.admin:
                self._is_writable = True
            else:
                row = conn.execute(
                    "SELECT 1 FROM user_playlist_write WHERE playlist=? AND user=?",
                    (name, user.user_id),
                ).fetchone()
                self._is_writable = row is not None

            row = conn.execute(
                "SELECT 1 FROM user_playlist_favorite WHERE playlist=? AND user=?",
                (name, user.user_id),
            ).fetchone()
            self._is_favorite = row is not None

    @override
    def __eq__(self, other: object):
        return isinstance(other, Playlist) and self.name == other.name

    @property
    def path(self) -> Path:
        return from_relpath(self.name)

    @property
    def is_primary(self) -> bool:
        assert self._is_primary is not None
        return self._is_primary

    @property
    def is_writable(self) -> bool:
        """Check if user is allowed to modify files in a playlist."""
        assert self._is_writable is not None
        return self._is_writable

    @property
    def is_favorite(self):
        assert self._is_favorite is not None
        return self._is_favorite

    async def choose_track(
        self,
        conn: Connection,
        user: auth.User | None,
        require_metadata: bool = False,
        tag_mode: TagMode | None = None,
        tags: list[str] | None = None,
    ) -> Track | None:
        """
        Randomly choose a track from this playlist
        Args:
            user: optionally specify a user to exclude tracks that this user has disliked
            require_metadata: only return tracks with at least some metadata (title, album, artists)
            tag_mode Tag mode (optional, must provide tags)
            tags: List of tags (optional, must provide tag_mode)
        Returns: Track object
        """
        # Select least recently played tracks
        query = "SELECT track.path, last_chosen FROM track WHERE playlist = ?"

        params: list[str | int] = [self.name]

        # don't choose disliked track
        if user is not None:
            query += " AND NOT EXISTS (SELECT 1 FROM dislikes WHERE user=? AND track=path)"
            params.append(user.user_id)

        # don't choose a track with reported problem
        query += " AND NOT EXISTS (SELECT 1 FROM track_problem WHERE track=path)"

        # tags
        track_tags_query = "SELECT tag FROM track_tag WHERE track = track.path"
        if tag_mode is TagMode.ALLOW:
            assert tags is not None
            query += " AND (" + " OR ".join(len(tags) * [f"? IN ({track_tags_query})"]) + ")"
            params.extend(tags)
        elif tag_mode is TagMode.DENY:
            assert tags is not None
            query += " AND (" + " AND ".join(len(tags) * [f"? NOT IN ({track_tags_query})"]) + ")"
            params.extend(tags)

        # metadata is required for guessing game
        if require_metadata:
            # Has at least metadata for: title, album, artists
            query += (
                " AND title NOT NULL AND album NOT NULL AND EXISTS(SELECT artist FROM track_artist WHERE track = path)"
            )

        query += f" ORDER BY last_chosen ASC LIMIT {self.track_count // 4  + 1}"

        # From selected least recently played tracks, choose a random one
        query = "SELECT * FROM (" + query + ") ORDER BY RANDOM() LIMIT 1"

        async with _TRACK_CHOOSE_LOCK:
            row = conn.execute(query, params).fetchone()
            if row is None:
                # No track found
                return None

            track, last_chosen = row
            current_timestamp = int(time.time())
            if last_chosen == 0:
                _LOGGER.info("chosen track: %s (never played)", track)
            else:
                hours_ago = (current_timestamp - last_chosen) / 3600
                _LOGGER.info("chosen track: %s (last played %.2f hours ago)", track, hours_ago)

            # it would be nice if this could be done in the background with create_task(), but that would cause
            # duplicate tracks to be chosen at times when the next track is chosen before last_chosen is updated
            conn.execute("UPDATE track SET last_chosen = ? WHERE path=?", (current_timestamp, track))

        return FileTrack(conn, track)

    def stats(self, conn: Connection) -> PlaylistStats:
        """Get playlist statistics"""
        return PlaylistStats(conn, self.name)

    def tracks(self, conn: Connection) -> list[Track]:
        """Get list of tracks in this playlist"""
        tracks: list[Track] = []
        for (relpath,) in conn.execute("SELECT path FROM track WHERE playlist = ?", (self.name,)):
            tracks.append(FileTrack(conn, relpath))
        return tracks


def get_playlists(conn: Connection, user: auth.User | None = None) -> list[Playlist]:
    names = [row[0] for row in conn.execute("SELECT name FROM playlist")]
    return [Playlist(conn, name, user) for name in names]


def check_path_writable(conn: Connection, user: auth.User, path: Path) -> Playlist:
    if path == settings.music_dir or path.parent == settings.music_dir:
        raise web.HTTPForbidden(reason="cannot write in root directory")

    playlist = Playlist(conn, relpath_playlist(to_relpath(path)), user)
    if not playlist.is_writable:
        raise web.HTTPForbidden(reason="no write access to playlist: " + playlist.name)
    return playlist
