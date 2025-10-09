import logging
import random
import time
from dataclasses import dataclass
from sqlite3 import Connection
from typing import cast

from raphson_mp.server import settings
from raphson_mp.server.playlist import Playlist
from raphson_mp.server.track import Track

log = logging.getLogger(__name__)


@dataclass
class RadioTrack:
    track: Track
    start_time: int

    @property
    def end_time(self):
        return self.start_time + self.track.duration * 1000


current_track: RadioTrack | None = None
next_track: RadioTrack | None = None


async def _choose_track(conn: Connection, previous_playlist: str | None = None) -> Track:
    if settings.radio_playlists:
        playlist_candidates = [
            p for p in settings.radio_playlists if len(settings.radio_playlists) == 1 or p != previous_playlist
        ]
    else:
        # if radio playlists are not configured, choose from playlists with at least one track
        playlist_candidates = [row[0] for row in conn.execute("SELECT playlist FROM track GROUP BY playlist")]

    playlist_name = random.choice(playlist_candidates)

    playlist = Playlist(conn, playlist_name)
    track = cast(Track, await playlist.choose_track(conn, None))
    return track


async def get_current_track(conn: Connection) -> RadioTrack:
    global current_track, next_track

    current_time = int(time.time() * 1000)

    # Normally when the radio is being actively listened to, a track will
    # have already been chosen. If this not the case, choose a track and
    # start it at a random point in time, to make it feel to the user
    # like the radio was playing continuously.

    if current_track is None:
        log.info("No current song, choose track starting at random time")
        track = await _choose_track(conn)
        start_time = current_time - int((track.duration * 1000) * random.random())
        current_track = RadioTrack(track, start_time)

    elif current_track.end_time <= current_time:
        if next_track is None:
            track = await _choose_track(conn)
            current_track = RadioTrack(track, current_time)
        else:
            current_track = next_track
            next_track = None

    return current_track


async def get_next_track(conn: Connection) -> RadioTrack:
    global current_track, next_track

    assert current_track

    if next_track is None:
        track = await _choose_track(conn)
        next_track = RadioTrack(track, current_track.end_time)

    return next_track
