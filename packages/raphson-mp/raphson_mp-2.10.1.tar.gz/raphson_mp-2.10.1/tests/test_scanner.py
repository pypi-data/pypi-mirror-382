import asyncio
import os
import secrets
import shutil
import time
from datetime import datetime, timedelta, timezone
from sqlite3 import Connection

from raphson_mp.client.playlist import Playlist
from raphson_mp.common.control import FileAction
from raphson_mp.server import scanner
from raphson_mp.server.track import from_relpath


def _check_scanner(conn: Connection, playlist: str, expected_relpath: str, expected_action: FileAction):
    # Verify last_change
    last_change = scanner.last_change(conn, playlist)
    global_last_change = scanner.last_change(conn, None)
    assert last_change == global_last_change
    assert datetime.now(tz=timezone.utc) - last_change < timedelta(seconds=5)

    # Verify scanner log
    action, relpath = conn.execute("SELECT action, track FROM scanner_log ORDER BY timestamp DESC LIMIT 1").fetchone()
    assert action == expected_action.value
    assert relpath == expected_relpath


async def test_scanner_file(playlist: Playlist, conn: Connection):
    relpath = f"{playlist.name}/{secrets.token_urlsafe()}.mp3"
    path = from_relpath(relpath)

    try:
        # Make sure scanner has nothing left to scan
        await scanner.scan(None, None)

        # Add file and scan again
        shutil.copy("tests/data/test.mp3", path)
        await scanner.scan(None, None)
        _check_scanner(conn, playlist.name, relpath, FileAction.INSERT)

        # Update file and scan again (must wait a second, scanner has whole second resolution)
        await asyncio.sleep(1)
        os.utime(path, (time.time(), time.time()))
        await scanner.scan(None, None)
        _check_scanner(conn, playlist.name, relpath, FileAction.UPDATE)

        # Delete file and scan again
        path.unlink()
        await scanner.scan(None, None)
        _check_scanner(conn, playlist.name, relpath, FileAction.DELETE)
    finally:
        path.unlink(missing_ok=True)


async def test_scanner_move_file(playlist: Playlist, conn: Connection):
    relpath_src = f"{playlist.name}/{secrets.token_urlsafe()}-src.mp3"
    relpath_dst = f"{playlist.name}/{secrets.token_urlsafe()}-dst.mp3"
    path_src = from_relpath(relpath_src)
    path_dst = from_relpath(relpath_dst)

    try:
        shutil.copy("tests/data/test.mp3", path_src)
        await scanner.scan(None, None)

        await scanner.move(None, path_src, path_dst)

        # check that file on disk has been moved
        assert not path_src.is_file()
        assert path_dst.is_file()

        # check scanner log
        _check_scanner(conn, playlist.name, relpath_dst, FileAction.MOVE)

        # clean up
        path_dst.unlink()
        await scanner.scan(None, None)
    finally:
        path_src.unlink(missing_ok=True)
        path_dst.unlink(missing_ok=True)
