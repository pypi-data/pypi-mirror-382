import asyncio
import json
import logging
from dataclasses import dataclass
from sqlite3 import Connection, Cursor
from typing import Any
from zipfile import ZIP_LZMA, ZipFile

from aiohttp import web

from raphson_mp.common import util
from raphson_mp.server import auth, db
from raphson_mp.server.decorators import route

_LOGGER = logging.getLogger(__name__)


def query_to_json(cursor: Cursor, one: bool = False) -> Any:
    # Based on: https://stackoverflow.com/a/3287775
    r = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    return (r[0] if r else None) if one else r


@dataclass
class ExportQuery:
    name: str
    query: str
    params: tuple[str | int] | tuple[()]
    one: bool


def generate_zip(queue_io: util.AsyncQueueIO, user_id: int):
    with db.MUSIC.connect() as conn:
        queries: list[ExportQuery] = [
            ExportQuery("user", "SELECT * FROM user WHERE id = ?", (user_id,), True),
            ExportQuery(
                "favorite_playlists", "SELECT playlist FROM user_playlist_favorite WHERE user = ?", (user_id,), False
            ),
            ExportQuery(
                "sessions",
                "SELECT creation_date, user_agent, remote_address, last_use FROM session WHERE user = ?",
                (user_id,),
                False,
            ),
            ExportQuery(
                "history",
                "SELECT timestamp, track, playlist, private FROM history WHERE user = ?",
                (user_id,),
                False,
            ),
            ExportQuery("dislikes", "SELECT track FROM dislikes WHERE user = ?", (user_id,), False),
            ExportQuery("shares", "SELECT share_code, create_timestamp FROM share WHERE user = ?", (user_id,), False),
            ExportQuery(
                "shares_tracks",
                "SELECT share.share_code, track_code, track FROM share_track JOIN share WHERE user = ?",
                (user_id,),
                False,
            ),
            ExportQuery("playlists", "SELECT name FROM playlist", (), False),
            ExportQuery("tracks", "SELECT * FROM track", (), False),
            ExportQuery("artists", "SELECT * FROM track_artist", (), False),
            ExportQuery("tags", "SELECT * FROM track_tag", (), False),
        ]

        with ZipFile(queue_io, "w") as zf:
            for query in queries:
                json_str = json.dumps(query_to_json(conn.execute(query.query, query.params), query.one), indent=4)
                zf.writestr(query.name + ".json", json_str, compress_type=ZIP_LZMA)

        queue_io.close()


@route("/data")
async def data(_request: web.Request, _conn: Connection, user: auth.User):
    queue_io = util.AsyncQueueIO()
    asyncio.create_task(asyncio.to_thread(generate_zip, queue_io, user.user_id))
    return web.Response(body=queue_io.iterator(), content_type="application/zip")
