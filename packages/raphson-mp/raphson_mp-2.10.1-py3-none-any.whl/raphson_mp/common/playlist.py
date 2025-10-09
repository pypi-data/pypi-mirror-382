from dataclasses import dataclass


@dataclass(kw_only=True)
class PlaylistBase:
    name: str
    track_count: int
