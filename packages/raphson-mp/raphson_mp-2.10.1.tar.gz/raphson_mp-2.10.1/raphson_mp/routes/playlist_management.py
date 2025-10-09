import asyncio
from sqlite3 import Connection

from aiohttp import web

from raphson_mp.common import metadata, util
from raphson_mp.server import spotify
from raphson_mp.server.auth import User
from raphson_mp.server.decorators import route
from raphson_mp.server.playlist import get_playlists
from raphson_mp.server.response import template


@route("")
async def route_playlists(_request: web.Request, conn: Connection, user: User):
    """
    Playlist management page
    """
    spotify_client = spotify.client()

    return await template(
        "playlist_management.jinja2",
        user_is_admin=user.admin,
        playlists=get_playlists(conn, user),
        spotify_available=spotify_client is not None,
    )


@route("/set_favorites", method="POST")
async def set_favorites(request: web.Request, conn: Connection, user: User):
    form = await request.post()
    playlists = [playlist for playlist in form.keys() if playlist != "csrf"]
    with conn:
        conn.execute("DELETE FROM user_playlist_favorite WHERE user = ?", (user.user_id,))
        conn.executemany(
            "INSERT INTO user_playlist_favorite VALUES (?, ?)", [(user.user_id, playlist) for playlist in playlists]
        )

    raise web.HTTPSeeOther("/playlist_management")


@route("/set_primary", method="POST")
async def set_primary(request: web.Request, conn: Connection, user: User):
    form = await request.post()
    playlist = form["playlist"]
    assert isinstance(playlist, str)
    if playlist == "":
        playlist = None
    conn.execute("UPDATE user SET primary_playlist = ? WHERE id = ?", (playlist, user.user_id))
    raise web.HTTPSeeOther("/playlist_management")


def _fuzzy_match_track(
    spotify_normalized_title: str, local_track_key: tuple[str, tuple[str, ...]], spotify_track: spotify.Track
) -> bool:
    (local_track_normalized_title, local_track_artists) = local_track_key
    if not util.str_match_approx(spotify_normalized_title, local_track_normalized_title):
        return False

    # Title matches, now check if artist matches (more expensive)
    for artist_a in spotify_track.artists:
        for artist_b in local_track_artists:
            if util.str_match_approx(artist_a, artist_b):
                return True

    return False


@route("/compare_spotify")
async def route_compare_spotify(request: web.Request, conn: Connection, _user: User):
    playlist_name = request.query["playlist"]
    spotify_playlist = request.query["spotify_playlist"]


    local_tracks: dict[tuple[str, tuple[str, ...]], tuple[str, list[str]]] = {}

    for title, artists in conn.execute(
        """
        SELECT title, GROUP_CONCAT(artist, ';') AS artists
        FROM track JOIN track_artist ON track.path = track_artist.track
        WHERE track.playlist = ?
        GROUP BY track.path
        """,
        (playlist_name,),
    ):
        local_track = (title, artists.split(";"))
        key = (metadata.normalize_title(title), tuple(local_track[1]))
        local_tracks[key] = local_track

    duplicate_check: set[str] = set()
    duplicates: list[spotify.Track] = []
    both: list[tuple[tuple[str, list[str]], spotify.Track]] = []
    only_spotify: list[spotify.Track] = []
    only_local: list[tuple[str, list[str]]] = []

    spotify_client = spotify.client()
    if spotify_client is None:
        raise web.HTTPBadRequest(text="Spotify API is not available")

    i = 0
    async for spotify_track in spotify_client.get_playlist(spotify_playlist):
        i += 1
        if i % 10 == 0:
            await asyncio.sleep(0)  # yield to event loop

        normalized_title = metadata.normalize_title(spotify_track.title)

        # Spotify duplicates
        duplicate_check_entry = spotify_track.display
        if duplicate_check_entry in duplicate_check:
            duplicates.append(spotify_track)
        duplicate_check.add(duplicate_check_entry)

        # Try to find fast exact match
        local_track_key = (normalized_title, tuple(spotify_track.artists))
        if local_track_key in local_tracks:
            local_track = local_tracks[local_track_key]
        else:
            # Cannot find exact match, look for partial match
            for local_track_key in local_tracks.keys():
                if _fuzzy_match_track(normalized_title, local_track_key, spotify_track):
                    break
            else:
                # no match found
                only_spotify.append(spotify_track)
                continue

        # match found, present in both
        both.append((local_tracks[local_track_key], spotify_track))
        del local_tracks[local_track_key]

    # any local tracks still left in the dict must have no matching spotify track
    only_local.extend(local_tracks.values())

    return await template(
        "spotify_compare.jinja2", duplicates=duplicates, both=both, only_local=only_local, only_spotify=only_spotify
    )
