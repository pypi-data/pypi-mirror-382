from dataclasses import dataclass

from raphson_mp.common.playlist import PlaylistBase


@dataclass(kw_only=True)
class Playlist(PlaylistBase):
    favorite: bool
    write: bool
