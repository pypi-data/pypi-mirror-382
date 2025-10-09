import asyncio
import logging
import os
import sys
from argparse import ArgumentParser
from collections.abc import Coroutine
from pathlib import Path
from typing import Any

from raphson_mp.cli import download
from raphson_mp.common.lyrics import PlainLyrics, TimeSyncedLyrics
from raphson_mp.server import auth, db, logconfig, offline_sync, scanner, settings
from raphson_mp.server.features import FEATURES, Feature
from raphson_mp.server.server import TaskScheduler

log = logging.getLogger("cli")


async def handle_start(args: Any) -> None:
    """
    Handle command to start server
    """
    from raphson_mp.server.server import Server

    settings.proxy_count = args.proxy_count
    settings.access_log = args.access_log

    if not os.getenv("MUSIC_HAS_RELOADED"):
        await db.migrate()

    server = Server(args.dev, enable_profiler=args.profiler, asyncio_debug=args.asyncio_debug)

    await server.start(args.host, args.port)


async def handle_useradd(args: Any) -> None:
    """
    Handle command to add user
    """
    username = args.username
    admin = bool(args.admin)
    password = input("Enter password:")

    with db.MUSIC.connect() as conn:
        await auth.User.create(conn, username, password, admin=admin)

    log.info("user added successfully")


async def handle_userdel(args: Any) -> None:
    """
    Handle command to delete user
    """
    with db.MUSIC.connect() as conn:
        deleted = conn.execute("DELETE FROM user WHERE username=?", (args.username,)).rowcount
        if deleted == 0:
            log.warning("No user deleted, does the user exist?")
        else:
            log.info("user deleted successfully")


async def handle_userlist(_args: Any) -> None:
    """
    Handle command to list users
    """
    with db.MUSIC.connect() as conn:
        result = conn.execute("SELECT username, admin FROM user")
        if result.rowcount == 0:
            log.info("no users")
            return

        log.info("users:")

        for username, is_admin in result:
            if is_admin:
                log.info("- %s (admin)", username)
            else:
                log.info("- %s", username)


async def handle_passwd(args: Any) -> None:
    """
    Handle command to change a user's password
    """
    with db.MUSIC.connect() as conn:
        result = conn.execute("SELECT id FROM user WHERE username=?", (args.username,)).fetchone()
        if result is None:
            print("No user exists with the provided username")
            return

        user_id = result[0]
        target_user = auth.User.get(conn, user_id=user_id)

        new_password = input("Enter new password:")
        await target_user.update_password(conn, new_password)

        print("Password updated successfully.")


async def handle_scan(_args: Any) -> None:
    """
    Handle command to scan playlists
    """
    await scanner.scan(None)


async def handle_migrate(_args: Any) -> None:
    """
    Handle command for database migration
    """
    await db.migrate()


async def handle_sync(args: Any) -> None:
    """
    Handle command for offline mode sync
    """
    if not settings.offline_mode:
        log.warning("Refusing to sync, music player is not in offline mode")
        return

    if args.playlists is not None:
        if args.playlists == "favorite":
            await offline_sync.change_playlists([])
            return

        playlists = args.playlists.split(",")
        await offline_sync.change_playlists(playlists)
        return

    sync = offline_sync.OfflineSync(offline_sync.CommandLineSyncProgress(), args.force_resync)
    await sync.run()


async def handle_download(args: Any) -> None:
    await download.start(args.playlist)


async def handle_cover(args: Any) -> None:
    from raphson_mp.server import album

    cover_bytes = await album._get_cover_data(args.artist, args.title, args.meme)  # pyright: ignore[reportPrivateUsage]
    if cover_bytes:
        Path("cover.jpg").write_bytes(cover_bytes.data)


async def handle_acoustid(args: Any) -> None:
    from raphson_mp.server import acoustid, musicbrainz

    fp = await acoustid.get_fingerprint(Path(args.path))
    log.info("duration: %s", fp["duration"])
    log.info("fingerprint: %s", fp["fingerprint"])

    results = await acoustid.lookup(fp)
    for result in results:
        log.info("result %s with score %s", result["id"], result["score"])

        for recording in result["recordings"]:
            async for meta in musicbrainz.get_recording_metadata(recording["id"]):
                log.info("recording: %s: %s", recording["id"], meta)


async def handle_lyrics(args: Any) -> None:
    from raphson_mp.server import lyrics

    lyrics = await lyrics.find_lyrics(args.title, args.artist, args.album, args.duration)

    if isinstance(lyrics, PlainLyrics):
        print(lyrics.text)
    elif isinstance(lyrics, TimeSyncedLyrics):
        print(lyrics.to_lrc())
    else:
        raise ValueError(lyrics)


async def handle_bing(args: Any) -> None:
    from raphson_mp.server import bing

    result = await bing.image_search(args.query)
    if result:
        Path("bing_result").write_bytes(result)
        log.info("saved to bing_result file")
    else:
        log.error("no result")


async def handle_maintenance(_args: Any) -> None:
    await TaskScheduler.maintenance()


def _strenv(name: str, default: str | None = None) -> str | None:
    return os.getenv("MUSIC_" + name, default)


def _intenv(name: str, default: int | None = None) -> int | None:
    text = _strenv(name, str(default) if default else None)
    if text is None:
        return default
    return int(text)


def _boolenv(name: str) -> bool:
    val = _strenv(name)
    if val is None:
        return False
    val = val.lower()
    if val in {"1", "true", "yes"}:
        return True
    elif val in {"0", "false", "no"}:
        return False
    else:
        raise ValueError("invalid boolean value: " + val)


def split_by_comma(inp: str | None) -> list[str]:
    if inp is None:
        return []
    return [s.strip() for s in inp.split(",") if s.strip() != ""]


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "--log-level",
        default=_strenv("LOG_LEVEL", settings.log_level),
        choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
        help="set log level for Python loggers",
    )
    parser.add_argument(
        "--short-log-format", action="store_true", default=_boolenv("SHORT_LOG_FORMAT"), help="use short log format"
    )
    parser.add_argument(
        "--data-dir",
        default=_strenv("DATA_DIR", _strenv("DATA_PATH", "./data")),
        help="path to directory where program data is stored",
    )
    parser.add_argument(
        "--blob-dir",
        default=_strenv("BLOB_DIR", None),
        help="path to directory where blob data is stored (optional, stored in data directory if not specified)",
    )
    parser.add_argument(
        "--music-dir", default=_strenv("MUSIC_DIR", "./music"), help="path to directory where music files are stored"
    )
    # error level by default to hide unfixable "deprecated pixel format used" warning
    parser.add_argument(
        "--ffmpeg-log-level",
        default=_strenv("FFMPEG_LOG_LEVEL", settings.ffmpeg_log_level),
        choices=("quiet", "fatal", "error", "warning", "info", "verbose", "debug"),
        help=f"log level for ffmpeg (default: {settings.ffmpeg_log_level})",
    )
    parser.add_argument("--track-max-duration-seconds", type=int, default=_intenv("TRACK_MAX_DURATION_SECONDS"))
    parser.add_argument(
        "--radio-playlists",
        default=_strenv("RADIO_PLAYLISTS"),
        help="comma-separated list of playlists to use for radio (if not specified, all playlists are used)",
    )
    parser.add_argument(
        "--lastfm-api-key",
        default=_strenv("LASTFM_API_KEY"),
        help="specify a last.fm API key to enable support for last.fm scrobbling",
    )
    parser.add_argument("--lastfm-api-secret", default=_strenv("LASTFM_API_SECRET"))
    parser.add_argument(
        "--spotify-api-id",
        default=_strenv("SPOTIFY_API_ID"),
        help="specify a Spotify API key to enable Spotify playlist comparison and artist images",
    )
    parser.add_argument("--spotify-api-secret", default=_strenv("SPOTIFY_API_SECRET"))
    parser.add_argument(
        "--offline",
        action="store_true",
        default=_boolenv("OFFLINE_MODE"),
        help="run in offline mode, using music synced from a primary music server",
    )
    parser.add_argument(
        "--news-server",
        default=_strenv("NEWS_SERVER"),
        help="news server url: https://github.com/Derkades/news-scraper",
    )
    parser.add_argument(
        "--bwrap",
        action="store_true",
        default=_boolenv("BWRAP"),
        help="use bubblewrap to sandbox subprocesses",
    )
    parser.add_argument(
        "--tracemalloc",
        action="store_true",
        default=_boolenv("TRACEMALLOC"),
        help="enable tracemalloc (for debugging unclosed resources)",
    )
    parser.add_argument(
        "--enable-features",
        type=str,
        default=None,
        help="specify features to enable as a comma separated list, choose from: "
        + ",".join([value.value for value in Feature]),
    )
    parser.add_argument(
        "--disable-features",
        type=str,
        default=None,
        help="specify features to disable as a comma separated list, choose from: "
        + ",".join([value.value for value in Feature]),
    )

    subparsers = parser.add_subparsers(required=True)

    cmd_start = subparsers.add_parser("start", help="start app in debug mode")
    cmd_start.add_argument("--host", default="127.0.0.1", help="interface to listen on")
    cmd_start.add_argument("--port", default=8080, type=int, help="port to listen on")
    cmd_start.add_argument(
        "--dev", action="store_true", help="run in development mode: enable auto reload, disable browser caching"
    )
    cmd_start.add_argument(
        "--profiler",
        action="store_true",
        default=_boolenv("PROFILER"),
        help="enable performance profiling (requires yappi)",
    )
    cmd_start.add_argument(
        "--proxy-count",
        type=int,
        default=_intenv("PROXY_COUNT", _intenv("PROXIES_X_FORWARDED_FOR", settings.proxy_count)),
        help="number of reverse proxies that add an IP address to X-Forwarded-For",
    )
    cmd_start.add_argument(
        "--asyncio-debug",
        action="store_true",
        default=_boolenv("ASYNCIO_DEBUG"),
        help="enable asyncio debug messages",
    )
    cmd_start.add_argument(
        "--access-log",
        action="store_true",
        default=_boolenv("ACCESS_LOG"),
        help="enable HTTP access logging",
    )
    cmd_start.set_defaults(func=handle_start)

    cmd_useradd = subparsers.add_parser("useradd", help="create new user")
    cmd_useradd.add_argument("username")
    cmd_useradd.add_argument("--admin", action="store_true", help="created user should have administrative rights")
    cmd_useradd.set_defaults(func=handle_useradd)

    cmd_userdel = subparsers.add_parser("userdel", help="delete a user")
    cmd_userdel.add_argument("username")
    cmd_userdel.set_defaults(func=handle_userdel)

    cmd_userlist = subparsers.add_parser("userlist", help="list users")
    cmd_userlist.set_defaults(func=handle_userlist)

    cmd_passwd = subparsers.add_parser("passwd", help="change password")
    cmd_passwd.add_argument("username")
    cmd_passwd.set_defaults(func=handle_passwd)

    cmd_scan = subparsers.add_parser("scan", help="scan playlists for changes")
    cmd_scan.set_defaults(func=handle_scan)

    cmd_migrate = subparsers.add_parser("migrate", help="run database migrations")
    cmd_migrate.set_defaults(func=handle_migrate)

    cmd_sync = subparsers.add_parser("sync", help="sync tracks from main server (offline mode)")
    cmd_sync.add_argument(
        "--force-resync",
        type=float,
        default=0.0,
        help="Ratio of randomly selected tracks to redownload even if up to date",
    )
    cmd_sync.add_argument(
        "--playlists",
        help="Change playlists to sync. Specify playlists as comma separated list without spaces. Enter 'favorite' to sync favorite playlists (default).",
    )
    cmd_sync.set_defaults(func=handle_sync)

    cmd_download = subparsers.add_parser(
        "download", help="download tracks from a remote server to a local directory in MP3 format"
    )
    cmd_download.add_argument(
        "playlist",
    )
    cmd_download.set_defaults(func=handle_download)

    cmd_debug_cover = subparsers.add_parser("debug-cover", help="for debugging: download cover image")
    cmd_debug_cover.add_argument("artist")
    cmd_debug_cover.add_argument("title")
    cmd_debug_cover.add_argument("--meme", action="store_true")
    cmd_debug_cover.set_defaults(func=handle_cover)

    cmd_debug_acoustid = subparsers.add_parser(
        "debug-acoustid", help="for debugging: calculate fingerprint and find track in AcoustID database"
    )
    cmd_debug_acoustid.add_argument("path")
    cmd_debug_acoustid.set_defaults(func=handle_acoustid)

    cmd_debug_lyrics = subparsers.add_parser("debug-lyrics", help="for debugging: find lyrics")
    cmd_debug_lyrics.add_argument("--title", required=True)
    cmd_debug_lyrics.add_argument("--artist", required=True)
    cmd_debug_lyrics.add_argument("--album")
    cmd_debug_lyrics.add_argument("--duration", type=int)
    cmd_debug_lyrics.set_defaults(func=handle_lyrics)

    cmd_debug_bing = subparsers.add_parser("debug-bing", help="for debugging: download cover image from bing")
    cmd_debug_bing.add_argument("query")
    cmd_debug_bing.set_defaults(func=handle_bing)

    cmd_debug_maintenance = subparsers.add_parser(
        "debug-maintenance", help="for debugging: run maintenance that normally runs periodically"
    )
    cmd_debug_maintenance.set_defaults(func=handle_maintenance)

    args = parser.parse_args()

    # Apply log configuration
    settings.log_level = args.log_level.upper()
    settings.log_short = args.short_log_format
    logconfig.apply()

    if args.ffmpeg_log_level:
        settings.ffmpeg_log_level = args.ffmpeg_log_level
    if args.track_max_duration_seconds:
        settings.track_max_duration_seconds = args.track_max_duration_seconds
    settings.radio_playlists = split_by_comma(args.radio_playlists)
    settings.lastfm_api_key = args.lastfm_api_key
    settings.lastfm_api_secret = args.lastfm_api_secret
    settings.spotify_api_id = args.spotify_api_id
    settings.spotify_api_secret = args.spotify_api_secret
    settings.offline_mode = args.offline
    if args.news_server:
        settings.news_server = args.news_server
    settings.bwrap = args.bwrap

    # features
    if args.enable_features is not None and args.disable_features is not None:
        log.error("--enable-features and --disable-features are mutually exclusive")
        sys.exit(1)
    elif args.enable_features is not None:
        FEATURES.clear()
        if args.enable_features != "":
            for feature_name in args.enable_features.split(","):
                FEATURES.add(Feature(feature_name))
    elif args.disable_features:
        for feature_name in args.disable_features.split(","):
            FEATURES.remove(Feature(feature_name))

    log.debug("enabled features: %s", ", ".join(feature.value for feature in FEATURES))

    # Data directory
    settings.data_dir = Path(args.data_dir).resolve()
    if not settings.data_dir.exists():
        log.error("data directory does not exist: %s", settings.data_dir.as_posix())
        log.info("path can be configured using the --data-dir flag or the MUSIC_DATA_DIR environment variable")
        log.info("if this is a fresh installation, please an empty directory")
        sys.exit(1)
    else:
        log.debug("data directory: %s", settings.data_dir.as_posix())

    # Music directory
    settings.music_dir = Path(args.music_dir).resolve() if not settings.offline_mode else None
    if settings.music_dir is not None:
        if not settings.music_dir.exists():
            log.error("music directory does not exist: %s", settings.music_dir.as_posix())
            log.info("path can be configured using the --music-dir flag or the MUSIC_MUSIC_DIR environment variable")
            log.info("if this is a fresh installation, please an empty directory")
            sys.exit(1)
        else:
            log.debug("music directory: %s", settings.music_dir.as_posix())

    # Blob directory
    if args.blob_dir:
        settings.blob_dir = Path(args.blob_dir).resolve()

        if not settings.blob_dir.exists():
            log.error("blob directory does not exist: %s", settings.blob_dir.as_posix())
            log.info("path can be configured using the --blob-dir flag or the MUSIC_BLOB_DIR environment variable")
            log.info("if this is a fresh installation, please an empty directory")
            sys.exit(1)
        else:
            log.debug("blob directory: %s", settings.blob_dir.as_posix())

    # Apply log configuration again, now that data_dir is configured
    logconfig.apply()

    # Verify consistent use of --offline
    mode_path = Path(settings.data_dir, 'mode')
    if mode_path.exists():
        mode = mode_path.read_text()
        if mode == 'offline':
            if not settings.offline_mode:
                log.error('this instance must be used with --offline')
                sys.exit(1)
        elif mode == 'online':
            if settings.offline_mode:
                log.error('this instance must be used without --offline')
                sys.exit(1)
        else:
            raise ValueError(mode)
    else:
        mode_path.write_text('offline' if settings.offline_mode else 'online')

    if args.tracemalloc:
        import tracemalloc

        tracemalloc.start()

    if isinstance(aw := args.func(args), Coroutine):
        asyncio.run(aw)
