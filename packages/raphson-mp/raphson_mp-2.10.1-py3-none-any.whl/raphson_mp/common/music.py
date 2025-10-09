from dataclasses import dataclass

from raphson_mp.common.typing import AlbumDict, ArtistDict


@dataclass
class Album:
    name: str
    artist: str | None
    track: str  # arbitrary track from the album, can be used to obtain a cover art image

    def to_dict(self) -> AlbumDict:
        return {"name": self.name, "artist": self.artist, "track": self.track}

    @classmethod
    def from_dict(cls, album_dict: AlbumDict):
        return cls(album_dict["name"], album_dict["artist"], album_dict["track"])


@dataclass
class Artist:
    name: str

    def to_dict(self) -> ArtistDict:
        return {"name": self.name}

    @classmethod
    def from_dict(cls, artist_dict: ArtistDict):
        return cls(artist_dict["name"])
