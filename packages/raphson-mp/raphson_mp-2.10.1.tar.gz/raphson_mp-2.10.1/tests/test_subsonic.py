import hashlib
import math
import random
import secrets
import time
from sqlite3 import Connection
from typing import cast

from raphson_mp.client.playlist import Playlist
from raphson_mp.client.track import Track
from raphson_mp.common.music import Album, Artist
from raphson_mp.routes import subsonic
from raphson_mp.routes.subsonic import from_id, to_id
from raphson_mp.server import activity
from tests import TEST_USERNAME, T_client


async def test_auth(http_client: T_client, auth_token: str):
    # No authentication
    async with http_client.get("/rest/ping") as response:
        response.raise_for_status()
        assert '<error code="42" />' in await response.text()

    # API key authentication
    async with http_client.get("/rest/ping", params={"apiKey": auth_token}) as response:
        response.raise_for_status()
        assert 'status="ok"' in await response.text()
    async with http_client.get("/rest/ping", params={"apiKey": auth_token, "u": "something"}) as response:
        response.raise_for_status()
        assert '<error code="43" />' in await response.text()
    async with http_client.get("/rest/ping", params={"apiKey": secrets.token_hex()}) as response:
        response.raise_for_status()
        assert '<error code="44" />' in await response.text()

    # Legacy authentication
    async with http_client.get("/rest/ping", params={"u": TEST_USERNAME, "p": auth_token}) as response:
        response.raise_for_status()
        assert 'status="ok"' in await response.text()
    async with http_client.get(
        "/rest/ping", params={"u": TEST_USERNAME, "p": "enc:" + auth_token.encode().hex()}
    ) as response:
        response.raise_for_status()
        assert 'status="ok"' in await response.text()
    async with http_client.get("/rest/ping", params={"u": TEST_USERNAME, "p": auth_token + "a"}) as response:
        response.raise_for_status()
        assert '<error code="40" />' in await response.text()

    # Hashed token authentication
    salt = secrets.token_hex()
    hash = hashlib.md5((auth_token + salt).encode()).hexdigest()
    async with http_client.get("/rest/ping", params={"u": TEST_USERNAME, "t": hash, "s": salt}) as response:
        response.raise_for_status()
        assert 'status="ok"' in await response.text()
    async with http_client.get("/rest/ping", params={"u": TEST_USERNAME, "t": hash, "s": salt + "a"}) as response:
        response.raise_for_status()
        assert '<error code="40" />' in await response.text()


async def _request(http_client: T_client, auth_token: str, endpoint: str, params: dict[str, str]):
    async with http_client.get(
        "/rest/" + endpoint, params={"apiKey": auth_token, "f": "json", "c": "Test", **params}
    ) as response:
        response.raise_for_status()
        return response


async def _request_json(http_client: T_client, auth_token: str, endpoint: str, params: dict[str, str]):
    async with http_client.get(
        "/rest/" + endpoint, params={"apiKey": auth_token, "f": "json", "c": "Test", **params}
    ) as response:
        response.raise_for_status()
        return (await response.json())["subsonic-response"]


async def test_id(track: Track, artist: Artist, album: Album, playlist: Playlist):
    assert from_id(to_id(track.path)) == track.path
    assert from_id(to_id(artist)) == artist
    assert from_id(to_id(album)) == album
    assert from_id(to_id(playlist.name)) == playlist.name


async def test_getOpenSubsonicExtensions(http_client: T_client, auth_token: str):
    await _request_json(http_client, auth_token, "getOpenSubsonicExtensions", {})


async def test_getArtists(http_client: T_client, auth_token: str):
    await _request(http_client, auth_token, "getArtists", {})


async def test_getArtist(http_client: T_client, auth_token: str, artist: Artist):
    artist_id = to_id(artist)
    response = await _request_json(http_client, auth_token, "getArtist", {"id": artist_id})
    assert cast(Artist, from_id(response["artist"]["id"])).name == artist.name
    assert response["artist"]["name"] == artist.name
    assert response["artist"]["coverArt"] == response["artist"]["id"]


async def test_getAlbumList2(http_client: T_client, auth_token: str):
    await _request_json(http_client, auth_token, "getAlbumList2", {"type": "random"})
    await _request_json(http_client, auth_token, "getAlbumList2", {"type": "newest"})
    await _request_json(http_client, auth_token, "getAlbumList2", {"type": "highest"})
    await _request_json(http_client, auth_token, "getAlbumList2", {"type": "frequent"})
    await _request_json(http_client, auth_token, "getAlbumList2", {"type": "recent"})
    await _request_json(
        http_client, auth_token, "getAlbumList2", {"type": "byYear", "fromYear": "2000", "toYear": "2010"}
    )
    await _request_json(http_client, auth_token, "getAlbumList2", {"type": "byGenre", "genre": "Pop"})
    await _request_json(http_client, auth_token, "getAlbumList2", {"type": "alphabeticalByName"})
    await _request_json(http_client, auth_token, "getAlbumList2", {"type": "alphabeticalByArtist"})


async def test_getCoverArt_album(http_client: T_client, auth_token: str, album: Album):
    await _request(http_client, auth_token, "getCoverArt", {"id": to_id(album)})


async def test_getCoverArt_track(http_client: T_client, auth_token: str, track: Track):
    await _request(http_client, auth_token, "getCoverArt", {"id": to_id(track.path)})


async def test_getAlbum(http_client: T_client, auth_token: str, album: Album):
    album_id = to_id(album)
    response = await _request_json(http_client, auth_token, "getAlbum", {"id": album_id})
    assert cast(Album, from_id(response["album"]["id"])).name == album.name
    assert cast(Album, from_id(response["album"]["id"])).artist == album.artist
    assert response["album"]["name"] == album.name
    assert response["album"]["coverArt"] == response["album"]["id"]
    assert response["album"]["songCount"] >= 1
    assert response["album"]["duration"] > 1
    assert response["album"]["sortName"]
    assert isinstance(response["album"]["isCompilation"], bool)


async def test_getSong(http_client: T_client, auth_token: str, track: Track):
    response = await _request_json(http_client, auth_token, "getSong", {"id": to_id(track.path)})
    assert cast(str, from_id(response["song"]["id"])) == track.path
    assert response["song"]["isDir"] == False
    assert response["song"]["duration"] > 1


async def test_stream(http_client: T_client, auth_token: str, track: Track):
    await _request(http_client, auth_token, "stream", {"id": to_id(track.path)})


async def test_download(http_client: T_client, auth_token: str, track: Track):
    await _request(http_client, auth_token, "stream", {"id": to_id(track.path)})


async def test_getLyrics():
    # TODO
    pass


async def test_getLyricsBySongId(http_client: T_client, auth_token: str, track: Track):
    await _request_json(http_client, auth_token, "getLyricsBySongId", {"id": to_id(track.path)})
    # TODO verify response contents


async def test_search3(http_client: T_client, auth_token: str):
    await _request_json(http_client, auth_token, "search3", {"query": "test"})


async def test_search3_all(http_client: T_client, auth_token: str):
    await _request_json(http_client, auth_token, "search3", {"query": ""})


async def test_getPlaylists(http_client: T_client, auth_token: str):
    await _request_json(http_client, auth_token, "getPlaylists", {})


async def test_getPlaylist(http_client: T_client, auth_token: str, playlist: Playlist):
    await _request_json(http_client, auth_token, "getPlaylist", {"id": to_id(playlist.name)})


async def test_scrobble(http_client: T_client, auth_token: str, track: Track, conn: Connection):
    await _request_json(http_client, auth_token, "scrobble", {"id": to_id(track.path)})
    now_playing_list = activity.now_playing()
    for now_playing in now_playing_list:
        if now_playing.data.track.get("path") == track.path:
            break
    else:
        assert False, now_playing_list

    # test that no history entry is created when submission is set to false
    row = conn.execute("SELECT timestamp FROM history ORDER BY timestamp DESC LIMIT 1").fetchone()
    assert row is None or row[0] < time.time() - 1


async def test_scrobble_submission(http_client: T_client, auth_token: str, track: Track, conn: Connection):
    await _request_json(http_client, auth_token, "scrobble", {"id": to_id(track.path), "submission": "true"})

    # a history entry should be created now
    row = conn.execute("SELECT track, timestamp FROM history ORDER BY timestamp DESC LIMIT 1").fetchone()
    assert row is not None
    assert row[0] == track.path
    assert math.isclose(row[1], time.time(), abs_tol=1)


async def test_getRandomSongs(http_client: T_client, auth_token: str):
    response = await _request_json(http_client, auth_token, "getRandomSongs", {"size": "5"})
    assert len(response["randomSongs"]["song"]) == 5


async def test_getRandomSongs_fromYear(http_client: T_client, auth_token: str):
    year = random.randint(1980, 2020)
    response = await _request_json(http_client, auth_token, "getRandomSongs", {"fromYear": str(year)})
    for song in response["randomSongs"]["song"]:
        assert song["year"] >= year


async def test_getRandomSongs_toYear(http_client: T_client, auth_token: str):
    year = random.randint(1980, 2020)
    response = await _request_json(http_client, auth_token, "getRandomSongs", {"toYear": str(year)})
    for song in response["randomSongs"]["song"]:
        assert song["year"] <= year


async def test_getGenres(http_client: T_client, auth_token: str):
    response = await _request_json(http_client, auth_token, "getGenres", {})
    assert isinstance(response["genres"]["genre"], list)


async def test_getSongsByGenre(http_client: T_client, auth_token: str, conn: Connection):
    track, tag = conn.execute("SELECT track, tag FROM track_tag LIMIT 1").fetchone()

    response = await _request_json(http_client, auth_token, "getSongsByGenre", {"genre": tag})
    for song in response["songsByGenre"]["song"]:
        if cast(str, from_id(song["id"])) == track:
            break
    else:
        assert False, response["songsByGenre"]["song"]


async def test_getStarred(http_client: T_client, auth_token: str):
    response = await _request_json(http_client, auth_token, "getStarred", {})
    assert response["starred"]["artist"] == []
    assert response["starred"]["album"] == []
    assert response["starred"]["song"] == []


async def test_getStarred2(http_client: T_client, auth_token: str):
    response = await _request_json(http_client, auth_token, "getStarred2", {})
    assert response["starred2"]["artist"] == []
    assert response["starred2"]["album"] == []
    assert response["starred2"]["song"] == []


async def test_getArtistInfo2(http_client: T_client, auth_token: str):
    response = await _request_json(http_client, auth_token, "getArtistInfo2", {})
    assert response["artistInfo2"] == {}


async def test_getAlbumInfo2(http_client: T_client, auth_token: str):
    response = await _request_json(http_client, auth_token, "getAlbumInfo2", {})
    assert response["albumInfo2"] == {}


async def test_getLicense(http_client: T_client, auth_token: str):
    response = await _request_json(http_client, auth_token, "getLicense", {})
    assert response["license"]["valid"] is True


async def test_getSimilarSongs2_track(http_client: T_client, auth_token: str, track: Track):
    await _request_json(http_client, auth_token, "getSimilarSongs2", {"id": to_id(track.path)})


async def test_getSimilarSongs2_artist(http_client: T_client, auth_token: str, artist: Artist):
    await _request_json(http_client, auth_token, "getSimilarSongs2", {"id": to_id(artist)})


async def test_tokenInfo(http_client: T_client, auth_token: str):
    response = await _request_json(http_client, auth_token, "tokenInfo", {})
    assert response["tokenInfo"]["username"] == TEST_USERNAME


async def test_startScan(http_client: T_client, auth_token: str):
    pass
    response = await _request_json(http_client, auth_token, "startScan", {})
    assert isinstance(response["scanStatus"]["scanning"], bool)
    assert isinstance(response["scanStatus"]["count"], int)
    assert subsonic.scan_task
    # wait for scanner to finish, or errors occur
    await subsonic.scan_task


async def test_getScanStatus(http_client: T_client, auth_token: str):
    response = await _request_json(http_client, auth_token, "getScanStatus", {})
    assert response["scanStatus"]["scanning"] is False
    assert isinstance(response["scanStatus"]["count"], int)
