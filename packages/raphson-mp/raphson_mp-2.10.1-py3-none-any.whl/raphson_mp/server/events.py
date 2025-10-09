from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from raphson_mp.common.control import FileAction
from raphson_mp.common.eventbus import Event

if TYPE_CHECKING:
    from raphson_mp.server.activity import NowPlaying
    from raphson_mp.server.auth import User
    from raphson_mp.server.track import Track


@dataclass
class NowPlayingEvent(Event):
    now_playing: NowPlaying


@dataclass
class StoppedPlayingEvent(Event):
    player_id: str


@dataclass
class TrackPlayedEvent(Event):
    user: User
    timestamp: int
    track: Track


@dataclass
class FileChangeEvent(Event):
    action: FileAction
    track: str
    user: User | None
