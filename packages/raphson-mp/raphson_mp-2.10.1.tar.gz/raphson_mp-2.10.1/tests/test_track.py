from pathlib import Path
from sqlite3 import Connection

from raphson_mp.server import track


def test_is_trashed():
    assert not track.is_trashed(Path("test"))
    assert track.is_trashed(Path(".trash.test"))
    assert track.is_trashed(Path(".trash.test/test"))


def test_filter_tracks(conn: Connection):
    # not a functional test, but ensures SQL has no syntax error
    for order in [None, "title", "ctime_asc", "year_desc", "random", "title,year"]:
        for has_metadata in [False, True]:
            track.filter_tracks(
                conn,
                10,
                0,
                playlist="test",
                artist="test",
                album_artist="test",
                album="test",
                year=1000,
                has_metadata=has_metadata,
                order=order,
            )
