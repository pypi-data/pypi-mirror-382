from sqlite3 import Connection

from raphson_mp.server import search

# low quality tests, but at least they ensure the SQL queries don't contain syntax errors


def test_search_tracks(conn: Connection):
    search.search_tracks(conn, "test")


def test_albums(conn: Connection):
    search.search_albums(conn, "test")
