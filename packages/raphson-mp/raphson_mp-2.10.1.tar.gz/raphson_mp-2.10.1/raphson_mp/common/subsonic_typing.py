from __future__ import annotations
from typing import NotRequired, TypedDict


# https://opensubsonic.netlify.app/docs/responses/itemgenre
class ItemGenre(TypedDict):
    pass


# https://opensubsonic.netlify.app/docs/responses/artistid3
class ArtistID3(TypedDict):
    id: str
    name: str
    coverArt: NotRequired[str]
    artistImageUrl: NotRequired[str]
    albumCount: NotRequired[int]
    starred: NotRequired[str]
    musicBrainzId: NotRequired[str]  # OpenSubsonic
    sortName: NotRequired[str]  # OpenSubsonic
    roles: NotRequired[list[str]]  # OpenSubsonic


# https://opensubsonic.netlify.app/docs/responses/artistwithalbumsid3/
class ArtistWithAlbumsID3(ArtistID3):
    album: list[AlbumID3]


# https://opensubsonic.netlify.app/docs/responses/child/
class Child(TypedDict):
    id: str
    parent: NotRequired[str]
    isDir: bool
    title: str
    album: NotRequired[str]
    artist: NotRequired[str]
    track: NotRequired[int]
    year: NotRequired[int]
    genre: NotRequired[str]
    coverArt: NotRequired[str]
    size: NotRequired[int]
    contentType: NotRequired[str]
    suffix: NotRequired[str]
    transcodedContentType: NotRequired[str]
    transcodedSuffix: NotRequired[str]
    duration: NotRequired[int]
    bitRate: NotRequired[int]
    path: NotRequired[str]
    isVideo: NotRequired[bool]
    userRating: NotRequired[int]
    averageRating: NotRequired[int]
    playCount: NotRequired[int]
    discNumer: NotRequired[int]
    created: NotRequired[str]
    starred: NotRequired[str]
    albumId: NotRequired[str]
    artistId: NotRequired[str]
    type: NotRequired[str]
    mediaType: NotRequired[str]  # OpenSubsonic
    bookmarkPosition: NotRequired[int]
    originalWidth: NotRequired[int]
    originalHeight: NotRequired[int]
    played: NotRequired[int]
    bpm: NotRequired[int]  # OpenSubsonic
    comment: NotRequired[int]  # OpenSubsonic
    sortName: NotRequired[int]  # OpenSubsonic
    musicBrainzId: NotRequired[int]  # OpenSubsonic
    isrc: NotRequired[list[int]]  # OpenSubsonic
    genres: NotRequired[ItemGenre]  # OpenSubsonic
    artists: NotRequired[ArtistID3]  # OpenSubsonic
    displayArtist: NotRequired[str]  # OpenSubsonic
    albumArtists: NotRequired[list[ArtistID3]]  # OpenSubsonic
    displayAlbumArtist: NotRequired[str]  # OpenSubsonic
    # contributors: NotRequired[list[Contributor]]  # OpenSubsonic
    displayComposer: NotRequired[str]  # OpenSubsonic
    moods: NotRequired[list[str]]  # OpenSubsonic
    # replayGain: NotRequired[ReplayGain]  # OpenSubsonic
    explicitStatus: NotRequired[str]  # OpenSubsonic


class RecordLabel(TypedDict):
    pass


class ItemDate(TypedDict):
    pass


class DiscTitle(TypedDict):
    pass


# https://opensubsonic.netlify.app/docs/responses/albumid3/
class AlbumID3(TypedDict):
    id: str
    name: str
    version: NotRequired[str]  # OpenSubsonic
    artist: NotRequired[str]
    artistId: NotRequired[str]
    coverArt: NotRequired[str]
    songCount: int
    duration: int
    playCount: NotRequired[int]
    created: str
    starred: NotRequired[str]
    year: NotRequired[int]
    genre: NotRequired[str]
    played: NotRequired[str]  # OpenSubsonic
    userRating: NotRequired[int]  # OpenSubsonic
    recordLabels: NotRequired[list[RecordLabel]]  # OpenSubsonic
    musicBrainzId: NotRequired[str]  # OpenSubonic
    geners: NotRequired[list[ItemGenre]]  # OpenSubonic
    artists: NotRequired[list[ArtistID3]]  # OpenSubonic
    displayArtist: NotRequired[str]  # OpenSubonic
    releaseTypes: NotRequired[list[str]]  # OpenSubonic
    moods: NotRequired[list[str]]  # OpenSubonic
    sortName: NotRequired[str]  # OpenSubonic
    originalReleaseDate: NotRequired[ItemDate]  # OpenSubonic
    releaseDate: NotRequired[ItemDate]  # OpenSubonic
    isCompilation: NotRequired[bool]  # OpenSubonic
    explicitStatus: NotRequired[str]  # OpenSubonic
    discTitles: NotRequired[list[DiscTitle]]  # OpenSubonic


# https://opensubsonic.netlify.app/docs/responses/albumid3withsongs/
class AlbumID3WithSongs(AlbumID3):
    song: list[Child]


# https://opensubsonic.netlify.app/docs/responses/playlist/
class Playlist(TypedDict):
    id: str
    name: str
    comment: NotRequired[str]
    owner: NotRequired[str]
    public: NotRequired[bool]
    songCount: int
    duration: int
    created: str
    changed: str
    coverArt: NotRequired[str]
    allowedUser: NotRequired[list[str]]


# https://opensubsonic.netlify.app/docs/responses/playlistwithsongs/
class PlaylistWithSongs(Playlist):
    entry: list[Child]
