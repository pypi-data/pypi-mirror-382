import re
from sqlite3 import Connection

from raphson_mp.common.music import Album, Artist
from raphson_mp.server.track import FileTrack, Track


def process_query(query: str) -> str:
    return '"' + re.sub(r"\s+", '" "', query.replace('"', '""')) + '"'


def search_tracks(conn: Connection, query: str, limit: int = 25, offset: int = 0) -> list[Track]:
    result = conn.execute(
        f"""
        SELECT track.path
        FROM track JOIN track_fts ON track.rowid = track_fts.rowid
        WHERE track_fts MATCH ? AND rank MATCH 'bm25(0.5, 2, 1, 1, 2, 0.1)'
        ORDER BY rank
        LIMIT {limit} OFFSET {offset}
        """,
        (process_query(query),),
    )
    return [FileTrack(conn, relpath) for relpath, in result]


def search_artists(conn: Connection, query: str, limit: int = 10, offset: int = 0) -> list[Artist]:
    result = conn.execute(
        f"""
        SELECT DISTINCT artist
        FROM track JOIN track_fts ON track.rowid = track_fts.rowid JOIN track_artist ON track.path = track_artist.track
        WHERE track_fts MATCH ?
        ORDER BY rank
        LIMIT {limit} OFFSET {offset}
        """,
        (process_query(query),),
    )
    return [Artist(row[0]) for row in result]


def search_albums(conn: Connection, query: str, limit: int = 10, offset: int = 0) -> list[Album]:
    return [
        Album(name, artist, track)
        for track, name, artist in conn.execute(
            f"""
            SELECT track.path, track.album, track.album_artist
            FROM track
            WHERE
                rowid = (
                    SELECT rowid
                    FROM track_fts
                    WHERE track_fts.album MATCH :query OR track_fts.album_artist MATCH :query OR track_fts.artists MATCH :query
                )
            GROUP BY track.album, track.album_artist
            LIMIT {limit} OFFSET {offset}
            """,
            {"query": process_query(query)},
        )
    ]
