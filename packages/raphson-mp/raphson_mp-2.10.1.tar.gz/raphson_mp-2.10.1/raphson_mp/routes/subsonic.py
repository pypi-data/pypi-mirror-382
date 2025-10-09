import asyncio
import base64
import hashlib
import hmac
import json
import logging
import shutil
import time
import xml.etree.ElementTree as ET
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from enum import Enum
from sqlite3 import Connection
from typing import Any, Never, cast

from aiohttp import web

from raphson_mp.common import const, metadata, util
from raphson_mp.common.control import ClientPlaying
from raphson_mp.common.image import ImageFormat, ImageQuality
from raphson_mp.common.lyrics import (
    INSTRUMENTAL_LYRICS,
    PlainLyrics,
    TimeSyncedLyrics,
    ensure_plain,
    parse_lyrics,
)
from raphson_mp.common.music import Album, Artist
from raphson_mp.common.subsonic_typing import (
    AlbumID3,
    AlbumID3WithSongs,
    ArtistID3,
    ArtistWithAlbumsID3,
    Child,
    Playlist as SubsonicPlaylist,
    PlaylistWithSongs,
)
from raphson_mp.common.track import AudioFormat
from raphson_mp.server import activity, auth, blob, db, scanner, search
from raphson_mp.server.artist import artist_image_thumbnail
from raphson_mp.server.auth import User
from raphson_mp.server.decorators import Route, simple_route
from raphson_mp.server.playlist import Playlist
from raphson_mp.server.track import FileTrack, Track

# https://www.subsonic.org/pages/api.jsprequest.config_dict[CONN]
# https://opensubsonic.netlify.app/docs/

_LOGGER = logging.getLogger(__name__)


class SubsonicError(Enum):
    GENERIC = 0
    PARAMETER_MISSING = 10
    CLIENT_INCOMPATIBLE = 20
    SERVER_INCOMPATIBLE = 30
    WRONG_USERNAME_OR_PASSWORD = 40
    TOKEN_AUTHENTICATION_NOT_SUPPORTED = 41
    AUTHENTICATION_MECHANISM_NOT_SUPPORTED = 42
    MULTIPLE_AUTHENTICATION = 43
    INVALID_API_KEY = 44
    USER_NOT_AUTHORIZED = 50
    TRIAL_PERIOD_OVER = 60
    REQUESTED_DATA_NOT_FOUND = 70


class SubsonicStatus(Enum):
    OK = "ok"
    FAILED = "failed"


def dict_to_xml(root: ET.Element, data: dict[str, Any]):
    for key, value in data.items():
        if type(value) == str:
            root.set(key, value)
        elif type(value) == int:
            root.set(key, str(value))
        elif type(value) == bool:
            root.set(key, "true" if value else "false")
        elif type(value) == dict:
            subtree = ET.Element(key)
            dict_to_xml(subtree, cast(dict[str, Any], value))
            root.append(subtree)
        elif type(value) == list:
            for item in cast(list[Any], value):
                if type(item) == dict:
                    subtree = ET.Element(key)
                    dict_to_xml(subtree, cast(dict[str, Any], item))
                    root.append(subtree)
                else:
                    _LOGGER.warning("cannot convert list item to xml: %s", item)
                    continue


def response(request: web.Request, data: dict[str, Any], status: SubsonicStatus = SubsonicStatus.OK):
    response_data: dict[str, Any] = {
        "subsonic-response": {
            "status": status.value,
            "version": "1.16.1",
            "type": "Raphson",
            "serverVersion": const.PACKAGE_VERSION,
            "openSubsonic": True,
            **data,
        }
    }

    f = request.query.get("f", "xml")

    if f == "xml":
        root = ET.Element("subsonic-response")
        dict_to_xml(root, response_data["subsonic-response"])
        xml = ET.tostring(root)
        return web.Response(body=xml, content_type="application/xml")

    if f == "json":
        return web.json_response(response_data)

    raise ValueError("invalid format: " + f)


def error(request: web.Request, error: SubsonicError) -> Never:
    resp = response(request, {"error": {"code": error.value}}, status=SubsonicStatus.FAILED)
    assert resp.body
    raise web.HTTPOk(text=resp.body.decode(), content_type=resp.content_type)


async def verify_auth(request: web.Request, conn: Connection) -> User:
    # API key authentication: https://opensubsonic.netlify.app/docs/extensions/apikeyauth/
    if "apiKey" in request.query:
        if "u" in request.query:
            error(request, SubsonicError.MULTIPLE_AUTHENTICATION)
        session = await auth.verify_token(request, request.query["apiKey"])
        if session is None:
            error(request, SubsonicError.INVALID_API_KEY)
        user = User.get(conn, session=session)
        return user

    # Legacy authentication
    if "u" in request.query and "p" in request.query:
        username = request.query["u"]
        password = request.query["p"]  # password is actually music player session token
        if password.startswith("enc:"):  # some clients send hex encoded password
            password = bytes.fromhex(password[4:]).decode()
        session = await auth.verify_token(request, password)
        if session is None:
            error(request, SubsonicError.WRONG_USERNAME_OR_PASSWORD)
        user = User.get(conn, session=session)
        assert user.username == username
        return user

    # Hashed token authentication
    if "t" in request.query:
        username = request.query["u"]
        hashed_token = request.query["t"]
        salt = request.query["s"]
        for (token,) in conn.execute(
            "SELECT token FROM session JOIN user ON user.id = user WHERE username = ?", (username,)
        ):
            if not hmac.compare_digest(hashlib.md5((token + salt).encode()).hexdigest(), hashed_token):
                continue
            session = await auth.verify_token(request, token)
            if not session:
                continue
            user = User.get(conn, session=session)
            return user
        _LOGGER.warning("no matching session token found")
        error(request, SubsonicError.WRONG_USERNAME_OR_PASSWORD)

    error(request, SubsonicError.AUTHENTICATION_MECHANISM_NOT_SUPPORTED)


SubsonicHandler = Callable[[web.Request, Connection, User], Awaitable[web.StreamResponse]]


def subsonic_route(path: str) -> Callable[[SubsonicHandler], Route]:
    def decorator(handler: SubsonicHandler) -> Route:
        async def wrapper(request: web.Request) -> web.StreamResponse:
            with db.MUSIC.connect() as conn:
                user = await verify_auth(request, conn)
                return await handler(request, conn, user)

        return Route(
            [
                web.route("GET", path, wrapper),
                # some clients append .view to the API method
                web.route("GET", path + ".view", wrapper),
            ]
        )

    return decorator


URLSAFE_ENCODE = bytes.maketrans(b"+/=", b"-_.")
URLSAFE_DECODE = bytes.maketrans(b"-_.", b"+/=")


def to_id(data: str | Album | Artist) -> str:
    if isinstance(data, str):  # playlist or track
        data_dict = {"type": "path", "path": data}
    elif isinstance(data, Album):
        data_dict = {"type": "album", "name": data.name, "artist": data.artist, "track": data.track}
    else:
        data_dict = {"type": "artist", "name": data.name}
    return base64.b64encode(json.dumps(data_dict).encode()).decode().translate(URLSAFE_ENCODE)


def from_id(b64: str) -> str | Album | Artist:
    assert b64
    data_dict = json.loads(base64.b64decode(b64.encode().translate(URLSAFE_DECODE)).decode())
    if data_dict["type"] == "path":
        return data_dict["path"]
    elif data_dict["type"] == "album":
        return Album(data_dict["name"], data_dict["artist"], data_dict["track"])
    elif data_dict["type"] == "artist":
        return Artist(data_dict["name"])
    else:
        raise ValueError()


def response_child(conn: Connection, track: Track, detailed: bool = False) -> Child:
    # https://opensubsonic.netlify.app/docs/responses/child/
    play_count = conn.execute("SELECT COUNT(*) FROM history WHERE track=?", (track.path,)).fetchone()[0]
    data: Child = {
        "id": to_id(track.path),
        "parent": track.playlist,
        "isDir": False,
        "title": track.title if track.title else track.display_title(),
        "coverArt": to_id(track.path),
        "duration": track.duration,
    }

    if primary_artist := track.primary_artist:
        data["artist"] = primary_artist
        data["artistId"] = to_id(Artist(primary_artist))
        data["displayArtist"] = primary_artist

    if track.album:
        data["album"] = track.album
        data["albumId"] = to_id(Album(track.album, track.album_artist, track.path))

    # TODO genres
    # TODO artists

    if detailed:
        data["parent"] = track.playlist
        data["suffix"] = track.path.split(".")[-1]
        data["transcodedContentType"] = AudioFormat.WEBM_OPUS_HIGH.content_type
        data["path"] = track.path
        data["mediaType"] = "song"
        data["playCount"] = play_count
        if track.year:
            data["year"] = track.year
        if track.tags:
            data["genre"] = track.tags[0]
        if track.track_number:
            data["track"] = track.track_number
        data["created"] = track.ctime_dt.isoformat()

    return data


def response_child_array(conn: Connection, count: int, offset: int) -> list[Child]:
    return [
        response_child(conn, FileTrack(conn, relpath))
        for relpath, in conn.execute(f"SELECT path FROM track LIMIT {count} OFFSET {offset}").fetchall()
    ]


# https://opensubsonic.netlify.app/docs/responses/albumid3/
def response_album(conn: Connection, album: Album) -> AlbumID3:
    total_count, total_duration, created, year = conn.execute(
        """
        SELECT COUNT(*), SUM(duration), MIN(ctime), MIN(year)
        FROM track
        WHERE album = ?
        """,
        (album.name,),
    ).fetchone()
    # TODO use album artist for matching

    data: AlbumID3 = {
        "id": to_id(album),
        "name": album.name,
        "coverArt": to_id(album),
        "songCount": total_count,
        "duration": total_duration,
        # genre TODO
        # genres TODO
        # displayArtist TODO
        "sortName": album.name,
        "isCompilation": metadata.album_is_compilation(album.name),
        "created": datetime.fromtimestamp(created, tz=timezone.utc).isoformat(),
    }

    if year:
        data["year"] = year

    if album.artist:
        data["artist"] = album.artist
        data["artistId"] = to_id(Artist(album.artist))

    return data


def response_album_with_songs(conn: Connection, album: Album) -> AlbumID3WithSongs:
    # https://opensubsonic.netlify.app/docs/responses/albumid3withsongs/

    query = "SELECT path FROM track WHERE album = ?"
    params: list[str] = [album.name]

    if album.artist:
        query += " AND album_artist = ?"
        params.append(album.artist)

    query += " GROUP BY title ORDER BY track_number ASC"

    return {
        **response_album(conn, album),
        "song": [response_child(conn, FileTrack(conn, path), detailed=True) for path, in conn.execute(query, params)],
    }


def response_artist(conn: Connection, name: str) -> ArtistWithAlbumsID3:
    # https://opensubsonic.netlify.app/docs/responses/artistwithalbumsid3/
    albums = [
        Album(album, album_artist, track)
        for album, album_artist, track in conn.execute(
            """
            SELECT album, album_artist, path
            FROM track JOIN track_artist ON path = track
            WHERE artist = ? AND album IS NOT NULL
            GROUP BY album
            """,
            (name,),
        )
    ]
    return {
        "id": to_id(Artist(name)),
        "name": name,
        "coverArt": to_id(Artist(name)),
        "albumCount": len(albums),
        "album": [response_album(conn, album) for album in albums],
    }


def response_artist_array(conn: Connection, count: int, offset: int) -> list[ArtistID3]:
    return [
        {
            "id": to_id(Artist(artist)),
            "coverArt": to_id(Artist(artist)),
            "name": artist,
        }
        for artist, in conn.execute(
            f"""
            SELECT artist
            FROM track_artist
            GROUP BY artist
            LIMIT {count} OFFSET {offset}
            """
        )
    ]


def response_playlist(conn: Connection, playlist: Playlist) -> SubsonicPlaylist:
    # https://opensubsonic.netlify.app/docs/responses/playlist

    return {
        "id": to_id(playlist.name),
        "name": playlist.name,
        "songCount": playlist.track_count,
        "duration": playlist.duration,
        "created": datetime.now(tz=timezone.utc).isoformat(),  # TODO
        "changed": scanner.last_change(conn, playlist.name).isoformat(),
    }


def response_playlist_with_songs(conn: Connection, playlist: Playlist) -> PlaylistWithSongs:
    return {
        **response_playlist(conn, playlist),
        "entry": [response_child(conn, track) for track in playlist.tracks(conn)],
    }


def response_playlist_array(conn: Connection, user: User) -> list[SubsonicPlaylist]:
    # https://opensubsonic.netlify.app/docs/responses/playlists

    return [
        response_playlist(conn, Playlist(conn, name))
        for name, in conn.execute("SELECT playlist FROM user_playlist_favorite WHERE user = ?", (user.user_id,))
    ]


def SubsonicGenre(conn: Connection, tag: str):
    song_count, album_count = conn.execute(
        "SELECT COUNT(DISTINCT path), COUNT(distinct ALBUM) FROM track JOIN track_tag ON path = track WHERE tag = ?",
        (tag,),
    )
    return {
        "value": tag,
        "songCount": song_count,
        "albumCount": album_count,
    }


def SubsonicArrayGenre(conn: Connection):
    return [
        {
            "value": tag,
            "songCount": song_count,
            "albumCount": album_count,
        }
        for tag, song_count, album_count in conn.execute(
            """
            SELECT tag, COUNT(DISTINCT path), COUNT(distinct ALBUM)
            FROM track JOIN track_tag ON path = track
            GROUP BY tag
            """
        )
    ]


@simple_route("/getOpenSubsonicExtensions", "/getOpenSubsonicExtensions.view")  # must be publicly accessible
async def getOpenSubsonicExtensions(request: web.Request):
    # https://opensubsonic.netlify.app/docs/endpoints/getopensubsonicextensions/
    data = {
        "openSubsonicExtensions": [
            {
                "name": "songLyrics",
                "versions": [1],
            },
        ],
    }
    return response(request, data)


@subsonic_route("/ping")
async def ping(request: web.Request, _conn: Connection, _user: User):
    return response(request, {})


@subsonic_route("/getArtists")
async def getArtists(request: web.Request, conn: Connection, _user: User):
    # https://opensubsonic.netlify.app/docs/endpoints/getartists/
    data: Any = {"artists": {"ignoredArticles": "The An A Die Das Ein Eine Les Le La", "index": []}}

    indices: Any = {}
    for (artist,) in conn.execute("SELECT artist FROM track_artist GROUP BY artist"):
        index = artist[:1].lower()
        if index not in indices:
            indices[index] = {"name": index, "artist": []}

        artist_id = to_id(Artist(artist))
        indices[index]["artist"].append({"id": artist_id, "name": artist, "coverArt": artist_id})

    for _index, value in indices.items():
        data["artists"]["index"].append(value)

    return response(request, data)


@subsonic_route("/getArtist")
async def getArtist(request: web.Request, conn: Connection, _user: User):
    # https://opensubsonic.netlify.app/docs/endpoints/getartist/

    # Tempo sometimes issues getArtist requests without id= specified (must be a bug?)
    if "id" not in request.query:
        return response(request, data={}, status=SubsonicStatus.FAILED)

    artist = from_id(request.query["id"])
    assert isinstance(artist, Artist)
    return response(request, {"artist": response_artist(conn, artist.name)})


@subsonic_route("/getAlbumList2")
async def getAlbumList2(request: web.Request, conn: Connection, user: User):
    # https://opensubsonic.netlify.app/docs/endpoints/getalbumlist2/
    t = request.query["type"]

    query = "SELECT album, album_artist, path"
    params: list[str | int] = []

    if t == "random":
        query += """
        FROM track
        WHERE album IS NOT NULL
        GROUP BY album
        ORDER BY RANDOM()
        """
    elif t == "newest":
        query += """
        FROM track
        WHERE album IS NOT NULL
        GROUP BY album
        ORDER BY ctime DESC
        """
    elif t == "highest":
        # not supported, return an empty list
        return response(request, {"albumList2": {"album": []}})
    elif t == "frequent":
        query += """
        FROM track JOIN history ON track.path = history.track
        WHERE album IS NOT NULL AND user = ?
        GROUP BY album
        ORDER BY COUNT(*) DESC
        """
        params.append(user.user_id)
    elif t == "recent":
        query += """
        FROM track JOIN history ON track.path = history.track
        WHERE album IS NOT NULL AND user = ?
        GROUP BY album
        ORDER BY timestamp DESC
        """
        params.append(user.user_id)
    elif t == "byYear":
        query += """
        FROM track
        WHERE album IS NOT NULL AND year >= ? AND year <= ?
        GROUP BY album
        ORDER BY year
        """
        params.extend((int(request.query["fromYear"]), int(request.query["toYear"])))
    elif t == "byGenre":
        query += """
        FROM track
        JOIN track_tag ON path = track
        WHERE album IS NOT NULL AND tag = ?
        GROUP BY album
        """
        params.append(request.query["genre"])
    elif t == "alphabeticalByName":
        query += """
        FROM track
        WHERE album IS NOT NULL
        GROUP BY album
        ORDER BY album ASC
        """
    elif t == "alphabeticalByArtist":
        query += """
        FROM track
        WHERE album IS NOT NULL
        GROUP BY album
        ORDER BY album_artist ASC
        """
    else:
        raise ValueError(t)

    size = int(request.query.get("size", 10))
    offset = int(request.query.get("offset", 0))
    query += f" LIMIT {size} OFFSET {offset}"

    data: Any = {
        "albumList2": {
            "album": [
                response_album(conn, Album(album, album_artist, track))
                for album, album_artist, track in conn.execute(query, params)
            ]
        }
    }

    return response(request, data)


@subsonic_route("/getCoverArt")
async def getCoverArt(request: web.Request, conn: Connection, _user: User):
    # https://opensubsonic.netlify.app/docs/endpoints/getcoverart/
    cover_id = from_id(request.query["id"])
    img_format = ImageFormat.JPEG
    img_quality = ImageQuality.LOW

    if isinstance(cover_id, Artist):
        cover_bytes = await artist_image_thumbnail(cover_id.name, img_format, img_quality)
    else:
        if isinstance(cover_id, Album):
            relpath = cover_id.track
        else:
            relpath = cover_id

        track = FileTrack(conn, relpath)
        cover_bytes = await track.get_cover(False, img_quality, img_format)

    return web.Response(body=cover_bytes, content_type=img_format.content_type)


@subsonic_route("/getAlbum")
async def getAlbum(request: web.Request, conn: Connection, _user: User):
    # https://opensubsonic.netlify.app/docs/endpoints/getalbum/
    album = from_id(request.query["id"])
    assert isinstance(album, Album)
    return response(request, {"album": response_album_with_songs(conn, album)})


@subsonic_route("/getSong")
async def getSong(request: web.Request, conn: Connection, _user: User):
    relpath = from_id(request.query["id"])
    assert isinstance(relpath, str)
    track = FileTrack(conn, relpath)
    return response(request, data={"song": response_child(conn, track, detailed=True)})


async def _stream_download(request: web.Request, conn: Connection):
    relpath = from_id(request.query["id"])
    assert isinstance(relpath, str)
    track = FileTrack(conn, relpath)
    return await blob.AudioBlob(track, AudioFormat.WEBM_OPUS_HIGH).response()


@subsonic_route("/stream")
async def stream(request: web.Request, conn: Connection, _user: User):
    # https://opensubsonic.netlify.app/docs/endpoints/stream/
    return await _stream_download(request, conn)


@subsonic_route("/download")
async def download(request: web.Request, conn: Connection, _user: User):
    # https://opensubsonic.netlify.app/docs/endpoints/download/
    # supposed to return original audio file without transcoding, but we return the transcoded file anyway
    # opus is good quality and storage is precious
    return await _stream_download(request, conn)


@subsonic_route("/getLyrics")
async def getLyrics(request: web.Request, conn: Connection, _user: User):
    # https://opensubsonic.netlify.app/docs/endpoints/getlyrics/
    if "artist" not in request.query or "title" not in request.query:
        _LOGGER.warning("received getLyrics request without title or without artist")
        return response(request, {}, status=SubsonicStatus.FAILED)

    artist = request.query["artist"]
    title = request.query["title"]

    plain_lyrics: PlainLyrics | None = None
    track: Track | None = None

    for (relpath,) in conn.execute(
        """
        SELECT path
        FROM track JOIN track_artist ON path = track
        WHERE title = ? AND artist = ?
        """,
        (title, artist),
    ).fetchall():
        track = FileTrack(conn, relpath)
        _LOGGER.info("found track for lyrics: %s", relpath)
        lyrics_text = track.lyrics
        parsed_lyrics = parse_lyrics(lyrics_text)
        plain_lyrics = ensure_plain(parsed_lyrics)
        if plain_lyrics is not None:
            break

    if plain_lyrics is None:
        plain_lyrics = INSTRUMENTAL_LYRICS

    data = {
        "lyrics": {
            "value": plain_lyrics.text,
        }
    }

    if track:
        if artist := track.primary_artist:
            data["lyrics"]["artist"] = artist
        if track.title:
            data["lyrics"]["title"] = track.title

    return response(request, data)


@subsonic_route("/getLyricsBySongId")
async def getLyricsBySongId(request: web.Request, conn: Connection, _user: User):
    # https://opensubsonic.netlify.app/docs/endpoints/getlyricsbysongid/
    relpath = from_id(request.query["id"])
    assert isinstance(relpath, str)
    track = FileTrack(conn, relpath)
    lyrics = track.parsed_lyrics

    lines: list[dict[str, str | int]] = []
    if isinstance(lyrics, TimeSyncedLyrics):
        for line in lyrics.text:
            lines.append({"start": int(line.start_time * 1000), "value": line.text})
    elif isinstance(lyrics, PlainLyrics):
        for line in lyrics.text.splitlines():
            lines.append({"value": line})
    else:
        # no lyrics
        return response(request, {"lyricsList": {"structuredLyrics": []}})

    data = {
        "lyricsList": {
            "structuredLyrics": [
                {
                    "lang": "und",
                    "synced": isinstance(lyrics, TimeSyncedLyrics),
                    "displayArtist": track.primary_artist,
                    "displayTitle": (
                        track.title if track.title else track.display_title(show_album=False, show_year=False)
                    ),
                    "line": lines,
                }
            ]
        }
    }
    return response(request, data)


@subsonic_route("/search3")
async def search3(request: web.Request, conn: Connection, _user: User):
    # https://opensubsonic.netlify.app/docs/endpoints/search3/
    query = request.query.get("query", "")
    artist_count = int(request.query.get("artistCount", 20))
    artist_offset = int(request.query.get("artistOffset", 0))
    album_count = int(request.query.get("albumCount", 20))
    album_offset = int(request.query.get("albumOffset", 0))
    song_count = int(request.query.get("songCount", 20))
    song_offset = int(request.query.get("songOffset", 0))

    if query == "":
        data = {
            "artist": response_artist_array(conn, artist_count, artist_offset),
            "album": [
                response_album(conn, Album(album, album_artist, track))
                for album, album_artist, track in conn.execute(
                    "SELECT album, album_artist, path FROM track WHERE album IS NOT NULL GROUP BY album, album_artist"
                )
            ],
            "song": response_child_array(conn, song_count, song_offset),
        }
    else:
        data = {
            "artist": [],  # TODO
            "album": [
                response_album(conn, album)
                for album in search.search_albums(conn, query, limit=album_count, offset=album_offset)
            ],
            "song": [
                response_child(conn, track, detailed=True)
                for track in search.search_tracks(conn, query, limit=song_count, offset=song_offset)
            ],
        }

    return response(request, {"searchResult3": data})


@subsonic_route("/getPlaylists")
async def getPlaylists(request: web.Request, conn: Connection, user: User):
    # https://opensubsonic.netlify.app/docs/endpoints/getplaylists/
    return response(request, {"playlists": {"playlist": response_playlist_array(conn, user)}})


@subsonic_route("/getPlaylist")
async def getPlaylist(request: web.Request, conn: Connection, _user: User):
    # https://opensubsonic.netlify.app/docs/endpoints/getplaylist/
    playlist_name = from_id(request.query["id"])
    assert isinstance(playlist_name, str)
    playlist = Playlist(conn, playlist_name)
    return response(request, {"playlist": response_playlist_with_songs(conn, playlist)})


@subsonic_route("/scrobble")
async def scrobble(request: web.Request, conn: Connection, user: User):
    # https://opensubsonic.netlify.app/docs/endpoints/scrobble/
    # TODO handle multiple id
    relpath = from_id(request.query["id"])
    assert isinstance(relpath, str)
    track = FileTrack(conn, relpath)
    submission = request.query.get("submission") == "true"
    client = request.query.get("c", "Subsonic")
    player_id = hashlib.sha256((user.username + client).encode()).hexdigest()

    data = ClientPlaying(track=track.to_dict(), paused=False, client=client)
    await activity.set_now_playing(user, player_id, 300, data)

    if submission:
        timestamp: int = int(request.query.get("time", time.time()))
        await activity.set_played(conn, user, track, timestamp)

    return response(request, {})


@subsonic_route("/getRandomSongs")
async def getRandomSongs(request: web.Request, conn: Connection, _user: User):
    size = int(request.query.get("size", 10))

    # TODO 'genre' and 'musicFolderId' filters

    query = "SELECT path FROM track WHERE true"
    params: list[str | int] = []

    if "fromYear" in request.query:
        query += " AND year >= ?"
        params.append(int(request.query["fromYear"]))

    if "toYear" in request.query:
        query += " AND year <= ?"
        params.append(int(request.query["toYear"]))

    query += " ORDER BY RANDOM()"
    query += f" LIMIT {size}"

    data = {
        "randomSongs": {
            "song": [
                response_child(conn, FileTrack(conn, relpath), detailed=True)
                for relpath, in conn.execute(query, params)
            ]
        }
    }

    return response(request, data)


@subsonic_route("/getGenres")
async def getGenres(request: web.Request, conn: Connection, _user: User):
    # https://opensubsonic.netlify.app/docs/endpoints/getgenres/
    return response(request, {"genres": {"genre": SubsonicArrayGenre(conn)}})


@subsonic_route("/getSongsByGenre")
async def getSongsByGenre(request: web.Request, conn: Connection, _user: User):
    # https://opensubsonic.netlify.app/docs/endpoints/getsongsbygenre/
    genre = request.query["genre"]
    count = int(request.query.get("count", 10))
    offset = int(request.query.get("offset", 0))

    data = {
        "songsByGenre": {
            "song": [
                response_child(conn, FileTrack(conn, relpath), detailed=True)
                for relpath, in conn.execute(
                    f"""
                    SELECT track
                    FROM track_tag
                    WHERE tag = ?
                    LIMIT {count} OFFSET {offset}
                    """,
                    (genre,),
                ).fetchall()
            ]
        }
    }

    return response(request, data)


@subsonic_route("/getStarred")
async def getStarred(request: web.Request, _conn: Connection, _user: User):
    # https://opensubsonic.netlify.app/docs/endpoints/getstarred/
    data: dict[str, Any] = {
        "starred": {
            "artist": [],
            "album": [],
            "song": [],
        }
    }
    return response(request, data)


@subsonic_route("/getStarred2")
async def getStarred2(request: web.Request, _conn: Connection, _user: User):
    # https://opensubsonic.netlify.app/docs/endpoints/getstarred/
    data: dict[str, Any] = {
        "starred2": {
            "artist": [],
            "album": [],
            "song": [],
        }
    }
    return response(request, data)


@subsonic_route("/getArtistInfo2")
async def getArtistInfo2(request: web.Request, _conn: Connection, _user: User):
    # https://opensubsonic.netlify.app/docs/endpoints/getartistinfo2/
    return response(request, {"artistInfo2": {}})


@subsonic_route("/getAlbumInfo2")
async def getAlbumInfo2(request: web.Request, _conn: Connection, _user: User):
    # https://opensubsonic.netlify.app/docs/endpoints/getalbuminfo2/
    return response(request, {"albumInfo2": {}})


@subsonic_route("/getLicense")
async def getLicense(request: web.Request, _conn: Connection, _user: User):
    # https://opensubsonic.netlify.app/docs/endpoints/getlicense/
    return response(request, {"license": {"valid": True}})


@subsonic_route("/getSimilarSongs2")
async def getSimilarSongs2(request: web.Request, conn: Connection, _user: User):
    # https://opensubsonic.netlify.app/docs/endpoints/getsimilarsongs2/
    # OpenSubsonic documents `id` to be the artist id, but in practice clients also use other ids like track id
    # https://github.com/CappielloAntonio/tempo/issues/326

    request_id = from_id(request.query["id"])
    count = int(request.query.get("count", 50))

    if isinstance(request_id, str):
        track = FileTrack(conn, request_id)
        rows = conn.execute(
            f"""
            SELECT path
            FROM track JOIN track_tag ON path = track_tag.track
            WHERE tag IN (
                SELECT tag
                FROM track_tag
                WHERE track = ?
            )
            ORDER BY RANDOM()
            LIMIT {count}
            """,
            (track.path,),
        ).fetchall()
    elif isinstance(request_id, Artist):
        rows = conn.execute(
            f"""
            SELECT path
            FROM track JOIN track_tag ON path = track_tag.track
            WHERE tag IN (
                SELECT tag
                FROM track_tag JOIN track_artist ON track_tag.track = track_artist.track
                WHERE artist = ?
            )
            ORDER BY RANDOM()
            LIMIT {count}
            """,
            (request_id.name,),
        ).fetchall()
    else:
        raise ValueError()

    data = {"similarSongs2": {"song": [response_child(conn, FileTrack(conn, relpath)) for relpath, in rows]}}
    return response(request, data)


@subsonic_route("/updatePlaylist")
async def updatePlaylist(request: web.Request, conn: Connection, user: User):
    playlist_name = from_id(request.query["playlistId"])
    assert isinstance(playlist_name, str)

    playlist = Playlist(conn, playlist_name, user)
    if not playlist.is_writable:
        raise web.HTTPForbidden(reason="no write access")

    for add in request.query.getall("songIdToAdd"):
        relpath = from_id(add)
        assert isinstance(relpath, str)
        track = FileTrack(conn, relpath)

        if track.playlist == playlist.name:
            continue

        await asyncio.to_thread(shutil.copy, track.path, playlist.path)

    util.create_task(scanner.scan_playlist(user, playlist.name))

    raise web.HTTPNoContent()


@subsonic_route("/tokenInfo")
async def tokenInfo(request: web.Request, _conn: Connection, user: User):
    data = {"tokenInfo": {"username": user.username}}
    return response(request, data)


scan_task: asyncio.Task[None] | None = None
scan_counter = scanner.Counter()


@subsonic_route("/startScan")
async def startScan(request: web.Request, _conn: Connection, user: User):
    global scan_task
    if scan_task is None or scan_task.done():
        scan_task = util.create_task(scanner.scan(user, scan_counter))
        scan_counter.count = 0
    return response(request, {"scanStatus": {"scanning": True, "count": scan_counter.count}})


@subsonic_route("/getScanStatus")
async def getScanStatus(request: web.Request, _conn: Connection, _user: User):
    is_scanning = scan_task is not None and not scan_task.done()
    return response(request, {"scanStatus": {"scanning": is_scanning, "count": scan_counter.count}})
