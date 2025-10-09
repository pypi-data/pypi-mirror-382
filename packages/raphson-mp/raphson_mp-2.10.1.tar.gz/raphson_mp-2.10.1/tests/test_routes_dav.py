import secrets
import shutil
from pathlib import Path
from sqlite3 import Connection
from urllib.parse import quote

from aiohttp import web

from raphson_mp.client.playlist import Playlist
from raphson_mp.common import util
from raphson_mp.server import track
from tests import playlist_write_access, user_admin

from .conftest import T_client


async def test_unauthorized(http_client_noauth: T_client):
    async with http_client_noauth.get("/dav") as response:
        assert response.status == web.HTTPUnauthorized.status_code
        assert "WWW-Authenticate" in response.headers


async def test_options(http_client: T_client):
    async with http_client.options("/dav") as response:
        assert "DAV" in response.headers
    async with http_client.options("/dav") as response:
        assert "DAV" in response.headers


async def test_propfind_root(http_client: T_client):
    async with http_client.request("PROPFIND", "/dav", headers={"Depth": "0"}) as response:
        assert response.status == 207
        assert response.content_type == "application/xml"
        # xml = ET.fromstring(await response.text())
        # assert len(xml.findall("d:href", {"d": "DAV:"})) == 1

    async with http_client.request("PROPFIND", "/dav", headers={"Depth": "1"}) as response:
        assert response.status == 207
        # xml = ET.fromstring(await response.text())
        # assert len(xml.findall("d:href", {"d": "DAV:"})) > 1

    async with http_client.request("PROPFIND", "/dav", headers={"Depth": "2"}) as response:
        assert response.status == web.HTTPBadRequest.status_code


async def test_propfind_404(http_client: T_client):
    async with http_client.request("PROPFIND", "/dav/I_DO_NOT_EXIST") as response:
        assert response.status == web.HTTPNotFound.status_code


async def test_propfind_file(http_client: T_client, track: track.Track):
    async with http_client.request("PROPFIND", f"/dav/{quote(track.path)}") as response:
        assert response.status == 207


async def test_get(http_client: T_client):
    test_path = track.from_relpath("test_file")
    try:
        # create file in root directory
        test_data = Path("docs/tyrone_music.jpg").read_bytes()
        test_path.write_bytes(test_data)

        # read from that file
        async with http_client.get("/dav/test_file") as response:
            assert test_data == await response.read()
    finally:
        test_path.unlink()


async def test_get_404(http_client: T_client):
    # file that does not exist should result in 404
    async with http_client.get("/dav/404notfound") as response:
        assert response.status == web.HTTPNotFound.status_code


async def test_put_root(http_client: T_client, conn: Connection):
    new_file_name = secrets.token_urlsafe()

    # we should not be able create a new file in the root directory
    async with http_client.put(f"/dav/{new_file_name}", data=b"hello") as response:
        assert response.status == web.HTTPForbidden.status_code

    async with http_client.put(f"/dav/./{new_file_name}", data=b"hello") as response:
        assert response.status == web.HTTPForbidden.status_code

    # not even with administrator privileges
    with user_admin(conn):
        async with http_client.put(f"/dav/{new_file_name}", data=b"hello") as response:
            assert response.status == web.HTTPForbidden.status_code

    assert not track.from_relpath(new_file_name).exists()


async def test_put_playlist(http_client: T_client, conn: Connection, playlist: Playlist):
    file_path = track.from_relpath(f"{playlist.name}/new_file")
    assert not file_path.exists()

    try:
        # uploading a file to a playlist should fail
        async with http_client.put("/dav/" + playlist.name + "/new_file", data=b"hello") as response:
            assert response.status == web.HTTPForbidden.status_code
        assert not file_path.exists()

        # try again, now with write permissions
        with playlist_write_access(conn, playlist):
            async with http_client.put("/dav/" + playlist.name + "/new_file", data=b"hello") as response:
                assert response.status == web.HTTPCreated.status_code
        assert file_path.is_file()
        assert file_path.read_bytes() == b"hello"
    finally:
        # clean up
        file_path.unlink()


async def test_delete_root(http_client: T_client, conn: Connection, playlist: Playlist):
    playlist_path = track.from_relpath(playlist.name)
    assert playlist_path.is_dir()

    # cannot delete files in the root, even with write access
    with playlist_write_access(conn, playlist):
        async with http_client.delete("/dav/" + playlist.name) as response:
            assert response.status == web.HTTPForbidden.status_code

    # cannot delete files in the root, even as administrator
    with user_admin(conn):
        async with http_client.delete("/dav/" + playlist.name) as response:
            assert response.status == web.HTTPForbidden.status_code

    # playlist should still exist
    assert playlist_path.is_dir()


async def test_delete(http_client: T_client, conn: Connection, playlist: Playlist):
    # create a file in a playlist
    new_file_name = secrets.token_urlsafe() + ".mp3"
    file_path = track.from_relpath(playlist.name + "/" + new_file_name)
    shutil.copy("tests/data/test.mp3", file_path)

    # cannot delete the file without write access
    async with http_client.delete(f"/dav/{playlist.name}/{new_file_name}") as response:
        assert response.status == web.HTTPForbidden.status_code
    assert file_path.is_file()  # file should still exist

    # can delete with write access
    with playlist_write_access(conn, playlist):
        async with http_client.delete(f"/dav/{playlist.name}/{new_file_name}") as response:
            assert response.status == web.HTTPNoContent.status_code

        # cannot delete file that is already deleted
        async with http_client.delete(f"/dav/{playlist.name}/{new_file_name}") as response:
            assert response.status == web.HTTPMethodNotAllowed.status_code

    assert not file_path.is_file()  # file should no longer exist

    # without permission, we should get 405 not 403
    async with http_client.delete(f"/dav/{playlist.name}/{new_file_name}") as response:
        assert response.status == web.HTTPMethodNotAllowed.status_code


async def test_mkcol(http_client: T_client, conn: Connection, playlist: Playlist):
    new_directory_name = secrets.token_urlsafe()
    url_path = f"{util.urlencode(playlist.name)}/{util.urlencode(new_directory_name)}"
    path = track.from_relpath(f"{playlist.name}/{new_directory_name}")

    assert not path.is_dir()

    try:
        # attempt to create directory without write access
        async with http_client.request("MKCOL", f"/dav/{url_path}") as response:
            assert response.status == web.HTTPForbidden.status_code

        assert not path.is_dir()

        with playlist_write_access(conn, playlist):
            # create directory
            async with http_client.request("MKCOL", f"/dav/{url_path}") as response:
                assert response.status == web.HTTPCreated.status_code

            # directory should now exist
            assert path.is_dir()

            # creating an already existing directory should fail with Conflict
            async with http_client.request("MKCOL", f"/dav/{url_path}") as response:
                assert response.status == web.HTTPConflict.status_code

    finally:
        # clean up
        path.rmdir()

    # TODO test creating a directory that already exists as a file


async def test_move_directory(http_client: T_client, playlist: Playlist, conn: Connection):
    src = f"{playlist.name}/{secrets.token_urlsafe()}-src"
    dst = f"{playlist.name}/{secrets.token_urlsafe()}-dst"

    src_path = track.from_relpath(src)
    dst_path = track.from_relpath(dst)

    try:
        src_path.mkdir()

        # attempt to move without write permissions
        async with http_client.request(
            "MOVE", f"/dav/{quote(src)}", headers={"Destination": f"/dav/{quote(dst)}"}
        ) as response:
            assert response.status == web.HTTPForbidden.status_code

        assert src_path.is_dir()
        assert not dst_path.is_dir()

        # move with write permission
        with playlist_write_access(conn, playlist):
            async with http_client.request(
                "MOVE", f"/dav/{quote(src)}", headers={"Destination": f"/dav/{quote(dst)}"}
            ) as response:
                assert response.status == web.HTTPNoContent.status_code
                assert dst_path.is_dir()
                assert not src_path.is_dir()
    finally:
        if src_path.is_dir():
            src_path.rmdir()
        if dst_path.is_dir():
            dst_path.rmdir()


# TODO test moving a file
