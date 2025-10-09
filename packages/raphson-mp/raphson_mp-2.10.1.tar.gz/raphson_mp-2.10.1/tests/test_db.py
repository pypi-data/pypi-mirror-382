import secrets
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from sqlite3 import Connection
from threading import Thread
from typing import cast

from raphson_mp.client.playlist import Playlist
from raphson_mp.server import db, settings
from tests import set_dirs


async def test_migrate():
    temp_fresh = Path(tempfile.mkdtemp("test_migrate_fresh"))
    temp_migrate = Path(tempfile.mkdtemp("test_migrate_migrate"))
    try:
        settings.data_dir = temp_fresh
        # Test database initialization completes without errors (e.g. no SQL syntax errors)
        await db.migrate()

        # Make sure auto vacuum is enabled
        for database in db.DATABASES:
            with database.connect() as conn:
                auto_vacuum = cast(int, conn.execute("PRAGMA auto_vacuum").fetchone()[0])
                assert auto_vacuum == 2

        settings.data_dir = temp_migrate

        # Initialize database how it would be when the migration system was first introduced
        # Not a great test because the tables have no content, but it's better than nothing.
        # db_version_0 files obtained from:
        # https://codeberg.org/raphson/music-server/src/commit/2c501187/src/sql
        for database in db.DATABASES:
            init_sql = (Path(__file__).parent / "db_version_0" / f"{database.name}.sql").read_text(encoding="utf-8")
            await database.create(init_sql=init_sql)

        # Run through all migrations
        await db.migrate()

        # Check that database is up to date
        with db.META.connect() as conn:
            version = cast(int, conn.execute("SELECT version FROM db_version").fetchone()[0])
            assert version == len(db.get_migrations())

        # Make sure the migrated tables are equal to fresh tables
        for db_name in db._BY_NAME:
            command = ["sqldiff", "--schema", Path(temp_fresh, f"{db_name}.db"), Path(temp_migrate, f"{db_name}.db")]
            output = subprocess.check_output(command)
            assert output == b"", output.decode()
    finally:
        set_dirs()  # restore original data directory settings
        shutil.rmtree(temp_fresh)
        shutil.rmtree(temp_migrate)


def test_version():
    assert db.get_version().startswith("3.")


def test_write_read():
    """
    This tests whether a read-only database connection sees changes made by a
    different connection, without needing to re-open the read-only database connection.
    """
    test_db_dir = Path(tempfile.mkdtemp())
    try:
        test_db = Path(test_db_dir, "test.db")

        with db._new_connection(test_db) as conn:
            conn.execute("CREATE TABLE test (test TEXT)")

        def reader():
            with db._new_connection(test_db) as conn:
                for _i in range(20):
                    row = cast(tuple[str] | None, conn.execute("SELECT * FROM test").fetchone())
                    if row:
                        assert row[0] == "hello"
                        return
                    time.sleep(0.1)

            raise ValueError("did not read value")

        thread = Thread(target=reader)
        thread.start()
        time.sleep(0.5)
        with db._new_connection(test_db, False) as conn:
            conn.execute('INSERT INTO test VALUES ("hello")')
        thread.join()
    finally:
        shutil.rmtree(test_db_dir)


def _search(conn: Connection, query: str) -> int | None:
    row = conn.execute("SELECT rowid FROM track_fts WHERE track_fts MATCH ?", ('"' + query + '"',)).fetchone()
    return None if row is None else row[0]


def test_fts_triggers(conn: Connection, playlist: Playlist):
    path = f"path-{secrets.token_urlsafe()}"
    title = f"title-{secrets.token_urlsafe()}"
    album = f"album-{secrets.token_urlsafe()}"
    album_artist = f"album_artist-{secrets.token_urlsafe()}"
    artist1 = f"artist1-{secrets.token_urlsafe()}"
    artist2 = f"artist2-{secrets.token_urlsafe()}"
    artist3 = f"artist3-{secrets.token_urlsafe()}"

    new_title = f"title-{secrets.token_urlsafe()}"
    new_album = f"album-{secrets.token_urlsafe()}"
    new_album_artist = f"album_artist-{secrets.token_urlsafe()}"

    try:
        # add track
        (rowid,) = conn.execute(
            """
            INSERT INTO track (path, playlist, duration, title, album, album_artist, mtime, ctime)
            VALUES (?, ?, 20, ?, ?, ?, 0, 0)
            RETURNING rowid
            """,
            (path, playlist.name, title, album, album_artist),
        ).fetchone()

        # add artists
        conn.execute("INSERT INTO track_artist VALUES (:p, :a1), (:p, :a2)", {"p": path, "a1": artist1, "a2": artist2})

        # we should now be able to find this track in FTS table
        for query in [path, title, album, album_artist, artist1, artist2]:
            assert _search(conn, query) == rowid

        # add one more artist
        conn.execute("INSERT INTO track_artist VALUES (?, ?)", (path, artist3))
        assert _search(conn, artist3) == rowid

        # modify track
        conn.execute(
            "UPDATE track SET title = ?, album = ?, album_artist = ? WHERE rowid = ?",
            (new_title, new_album, new_album_artist, rowid),
        )
        # we should no longer able to find the track using the previous values
        for query in [title, album, album_artist]:
            assert _search(conn, query) is None

        # but we should be able to find it using the new values
        for query in [new_title, new_album, new_album_artist]:
            assert _search(conn, query) == rowid

        # delete track
        conn.execute("DELETE FROM track WHERE path = ?", (path,))

        # make sure it is also deleted from track_fts
        assert _search(conn, path) is None

    finally:
        # clean up (only if test failed, otherwise it is already cleaned up)
        conn.execute("DELETE FROM track WHERE path = ?", (path,))
