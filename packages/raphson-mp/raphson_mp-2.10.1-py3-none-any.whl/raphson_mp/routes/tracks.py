import logging
from datetime import datetime
from sqlite3 import Connection

from aiohttp import web

from raphson_mp.common.typing import FilterResponseDict
from raphson_mp.server import scanner, search, track
from raphson_mp.server.auth import User
from raphson_mp.server.decorators import route

log = logging.getLogger(__name__)


@route("/filter")
async def route_filter(request: web.Request, conn: Connection, _user: User):
    order = request.query.get("order", None)

    # reuse previous response, except in case of random where a different result is expected every time
    last_modified: datetime | None = None
    if order != "random":
        last_modified = scanner.last_change(conn, request.query.get("playlist"))

        if request.if_modified_since and last_modified <= request.if_modified_since:
            raise web.HTTPNotModified()

    has_metadata = None
    if "has_metadata" in request.query:
        if request.query["has_metadata"] == "0":
            has_metadata = False
        elif request.query["has_metadata"] == "1":
            has_metadata = True

    tracks = track.filter_tracks(
        conn,
        limit=int(request.query.get("limit", 5000)),
        offset=int(request.query.get("offset", 0)),
        playlist=request.query.get("playlist"),
        artist=request.query.get("artist"),
        tag=request.query.get("tag"),
        album_artist=request.query.get("album_artist"),
        album=request.query.get("album"),
        year=int(request.query["year"]) if "year" in request.query else None,
        title=request.query.get("title"),
        has_metadata=has_metadata,
        order=order,
    )

    filter_response: FilterResponseDict = {"tracks": [track.to_dict() for track in tracks]}
    response = web.json_response(filter_response)
    response.last_modified = last_modified
    response.headers["Cache-Control"] = "no-cache"  # always verify last-modified
    return response


@route("/search")
async def route_search(request: web.Request, conn: Connection, _user: User):
    query = request.query["query"]
    tracks = search.search_tracks(conn, query)
    artists = search.search_artists(conn, query)
    albums = search.search_albums(conn, query)
    return web.json_response(
        {
            "tracks": [track.to_dict() for track in tracks],
            "artists": [artist.to_dict() for artist in artists],
            "albums": [album.to_dict() for album in albums],
        }
    )


@route("/tags")
async def route_tags(_request: web.Request, conn: Connection, _user: User):
    result = conn.execute("SELECT DISTINCT tag FROM track_tag ORDER BY tag")
    tags = [row[0] for row in result]
    return web.json_response(tags)
