import random
from collections.abc import AsyncIterator
from sqlite3 import Connection
from typing import cast

import pytest
from aiohttp.test_utils import BaseTestServer, TestClient, TestServer

from raphson_mp.client import RaphsonMusicClient
from raphson_mp.client.playlist import Playlist
from raphson_mp.client.track import Track
from raphson_mp.common.music import Album, Artist
from raphson_mp.common.typing import GetCsrfResponseDict, LoginResponseDict
from raphson_mp.server import auth, db
from raphson_mp.server.server import Server

from . import TEST_PASSWORD, TEST_USERNAME, T_client

_csrf_token = None


@pytest.fixture()
async def test_server() -> AsyncIterator[BaseTestServer]:
    server = Server(False)
    async with TestServer(server.app) as test_server:
        yield test_server


@pytest.fixture()
async def http_client_noauth(test_server: TestServer) -> AsyncIterator[T_client]:
    async with TestClient(test_server) as client:
        yield client


@pytest.fixture()
async def http_client(http_client_noauth: T_client) -> AsyncIterator[T_client]:
    async with http_client_noauth.post(
        "/auth/login", data={"username": TEST_USERNAME, "password": TEST_PASSWORD}, allow_redirects=False
    ) as response:
        assert response.status == 303

    yield http_client_noauth


@pytest.fixture
async def client(http_client_noauth: T_client) -> AsyncIterator[RaphsonMusicClient]:
    global _csrf_token
    async with http_client_noauth.post(
        "/auth/login", json={"username": TEST_USERNAME, "password": TEST_PASSWORD}, raise_for_status=True
    ) as response:
        response_dict = cast(LoginResponseDict, await response.json())
        token = response_dict["token"]
        _csrf_token = response_dict["csrf"]

    client = RaphsonMusicClient()
    base_url = str(http_client_noauth._server._root)
    await client.setup(base_url=base_url, token=token, user_agent="client test suite")
    yield client
    await client.close()


@pytest.fixture
async def csrf_token(http_client: T_client):
    async with http_client.get("/auth/get_csrf") as response:
        assert response.status == 200, await response.text()
        json_response = cast(GetCsrfResponseDict, await response.json())
    return json_response["token"]


# @pytest.fixture()
# async def playlist():
#     playlist_name = "test-" + random.randbytes(8).hex()
#     playlist_path = Path(settings.music_dir, playlist_name)
#     try:
#         playlist_path.mkdir()
#         await scanner.scan_playlists()
#         # give user write access to newly created playlist
#         with db.connect() as conn:
#             (user_id,) = conn.execute("SELECT id FROM user WHERE username=?", (TEST_USERNAME,)).fetchone()
#             conn.execute("INSERT INTO user_playlist_write VALUES (?, ?)", (user_id, playlist_name))
#         yield playlist_name
#     finally:
#         shutil.rmtree(playlist_path)
#         await scanner.scan_playlists()


# @pytest.fixture()
# async def track(playlist: Playlist):
#     path = Path(settings.music_dir, playlist, random.randbytes(4).hex() + ".ogg")
#     async with aiohttp.ClientSession() as session:
#         async with session.get("https://downloads.rkslot.nl/cipher.ogg") as response:
#             assert response.status == 200
#             path.write_bytes(await response.read())
#     with db.connect(read_only=True) as conn:
#         await scanner.scan_playlist(None, music.Playlist.by_name(conn, playlist))
#     yield music.to_relpath(path)


@pytest.fixture()
async def playlist(client: RaphsonMusicClient) -> Playlist:
    return random.choice(await client.playlists())


@pytest.fixture()
async def nonempty_playlist(client: RaphsonMusicClient) -> Playlist:
    return random.choice([p for p in await client.playlists() if p.track_count > 0])


@pytest.fixture()
async def track(client: RaphsonMusicClient, nonempty_playlist: Playlist) -> Track:
    return await client.choose_track(nonempty_playlist)


@pytest.fixture()
def artist(conn: Connection):
    artist = conn.execute("SELECT artist FROM track_artist ORDER BY RANDOM() LIMIT 1").fetchone()[0]
    return Artist(artist)


@pytest.fixture()
def album(conn: Connection):
    album, artist, track = conn.execute(
        "SELECT album, album_artist, path FROM track WHERE album IS NOT NULL ORDER BY RANDOM() LIMIT 1"
    ).fetchone()
    return Album(album, artist, track)


@pytest.fixture()
async def conn():
    with db.MUSIC.connect() as conn:
        yield conn


@pytest.fixture()
def auth_token(conn: Connection):
    return cast(
        str,
        conn.execute(
            "SELECT token FROM session JOIN user ON session.user = user.id WHERE username = ? LIMIT 1", (TEST_USERNAME,)
        ).fetchone()[0],
    )


@pytest.fixture
def user(conn: Connection):
    user_id = cast(int, conn.execute("SELECT id FROM user WHERE username = ?", (TEST_USERNAME,)).fetchone()[0])
    return auth.User.get(conn, user_id=user_id)
