from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from sqlite3 import Connection
from typing import cast

from raphson_mp.common import eventbus
from raphson_mp.common.control import ClientPlaying, ServerPlaying
from raphson_mp.common.track import NoSuchTrackError
from raphson_mp.server import auth, events, lastfm
from raphson_mp.server import track as server_track

_LOGGER = logging.getLogger(__name__)


@dataclass
class NowPlaying:
    player_id: str
    user_id: int
    username: str
    update_time: float
    lastfm_update_time: float
    expiry: int
    data: ClientPlaying

    def control_command(self) -> ServerPlaying:
        position = self.data.position
        if not self.data.paused and position is not None and self.data.duration is not None:
            # extrapolate current position
            position = min(self.data.duration, position + time.time() - self.update_time)

        return ServerPlaying(
            player_id=self.player_id,
            username=self.username,
            paused=self.data.paused,
            position=position,
            duration=self.data.duration,
            control=self.data.control,
            volume=self.data.volume,
            expiry=self.expiry,
            client=self.data.client,
            track=self.data.track,
            queue=self.data.queue,
            playlists=self.data.playlists,
        )


_NOW_PLAYING: dict[str, NowPlaying] = {}


def now_playing() -> list[NowPlaying]:
    current_time = int(time.time())
    return [entry for entry in _NOW_PLAYING.values() if entry.update_time > current_time - entry.expiry]


async def set_now_playing(
    user: auth.User,
    player_id: str,
    expiry: int,
    data: ClientPlaying,
) -> None:
    current_time = time.time()
    username = user.nickname if user.nickname else user.username

    now_playing = _NOW_PLAYING[player_id] = NowPlaying(
        player_id,
        user.user_id,
        username,
        current_time,
        current_time,
        expiry,
        data,
    )

    if not data.paused and now_playing.lastfm_update_time < current_time - 60:
        user_key = lastfm.get_user_key(cast(auth.StandardUser, user))
        if user_key:
            track = server_track.Track.from_dict(data.track)
            try:
                await lastfm.update_now_playing(user_key, track)
                now_playing.lastfm_update_time = current_time
            except NoSuchTrackError:
                pass

    await eventbus.fire(events.NowPlayingEvent(now_playing))


async def set_played(conn: Connection, user: auth.User, track: server_track.Track, timestamp: int):
    private = user.privacy == auth.PrivacyOption.AGGREGATE

    if not private:
        await eventbus.fire(events.TrackPlayedEvent(user, timestamp, track))

    conn.execute(
        """
        INSERT INTO history (timestamp, user, track, playlist, private)
        VALUES (?, ?, ?, ?, ?)
        """,
        (timestamp, user.user_id, track.path, track.playlist, private),
    )

    # last.fm requires track length to be at least 30 seconds
    if not private and track.duration >= 30:
        lastfm_key = lastfm.get_user_key(cast(auth.StandardUser, user))
        if lastfm_key:
            await lastfm.scrobble(lastfm_key, track, timestamp)


async def stop_playing(user: auth.User, player_id: str):
    playing = _NOW_PLAYING.get(player_id)
    if playing is None:
        return

    if playing.user_id != user.user_id:
        _LOGGER.warning("user %s attempted to stop player owned by different user %s", user.username, playing.user_id)
        return

    _LOGGER.debug("player %s stopped playing", player_id)
    del _NOW_PLAYING[player_id]
    await eventbus.fire(events.StoppedPlayingEvent(player_id))


async def remove_expired_playing():
    current_time = time.time()
    to_remove: list[str] = []
    for key, entry in _NOW_PLAYING.items():
        if entry.update_time + entry.expiry < current_time:
            _LOGGER.info("player expired: %s", key)
            to_remove.append(key)
            await eventbus.fire(events.StoppedPlayingEvent(key))

    for key in to_remove:
        del _NOW_PLAYING[key]
