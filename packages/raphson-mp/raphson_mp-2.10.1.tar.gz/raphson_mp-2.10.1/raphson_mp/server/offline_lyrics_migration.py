import asyncio
import html
import json
import logging
from sqlite3 import Connection
from raphson_mp.common.lyrics import INSTRUMENTAL_TEXT, LyricsLine, TimeSyncedLyrics, lyrics_to_text
from raphson_mp.server import db
from raphson_mp.server.track import FileTrack


_LOGGER = logging.getLogger(__name__)


def _migrate(conn: Connection, conn_offline: Connection, track: FileTrack):
    lyrics_json_str: str = conn_offline.execute(
        "SELECT lyrics_json FROM content WHERE path=?", (track.path,)
    ).fetchone()[0]
    lyrics_json = json.loads(lyrics_json_str)
    if "found" in lyrics_json and lyrics_json["found"]:
        # Legacy HTML lyrics, best effort conversion from HTML to plain text
        lyrics = html.unescape(lyrics_json["html"].replace("\n", "").replace("<br>", "\n"))
    elif "lyrics" in lyrics_json and "source_url" in lyrics_json and lyrics_json["lyrics"] is not None:
        # Legacy plaintext lyrics (before 2024-10)
        lyrics = lyrics_json["lyrics"]
    elif "type" in lyrics_json:
        # Newest type of legacy lyrics (before 2025-08-04)
        if lyrics_json["type"] == "plain":
            lyrics = lyrics_json["text"]
        elif lyrics_json["type"] == "synced":
            lines = [LyricsLine(line["start_time"], line["text"]) for line in lyrics_json["text"]]
            lyrics = lyrics_to_text(TimeSyncedLyrics(text=lines))
        else:
            lyrics = INSTRUMENTAL_TEXT
    else:
        lyrics = INSTRUMENTAL_TEXT

    # set lyrics
    track.lyrics = lyrics
    conn.execute("UPDATE track SET lyrics = ? WHERE path = ?", (lyrics, track.path))


async def migrate_task():
    with db.MUSIC.connect() as conn, db.OFFLINE.connect() as conn_offline:
        while True:
            row = conn.execute("SELECT path FROM track WHERE lyrics IS NULL LIMIT 1").fetchone()
            if row is None:
                _LOGGER.info("all lyrics are migrated")
                break

            (relpath,) = row
            _LOGGER.info("migrating lyrics: %s", relpath)
            track = FileTrack(conn, relpath)
            _migrate(conn, conn_offline, track)

            await asyncio.sleep(.01) # leave time for the server to do other things
