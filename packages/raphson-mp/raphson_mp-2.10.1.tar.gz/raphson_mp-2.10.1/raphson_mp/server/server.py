from __future__ import annotations

import asyncio
import importlib
import inspect
import logging
import os
import random
import shutil
import signal
import time
import weakref
from collections.abc import Awaitable, Callable
from typing import Final

import jinja2
from aiohttp import web
from aiohttp.log import access_logger
from aiohttp.typedefs import Middleware
from attr import dataclass

from raphson_mp.common import httpclient, util
from raphson_mp.common.track import TRASH_PREFIX
from raphson_mp.server import auth, blob, cache, db, i18n, middlewares, scanner, settings
from raphson_mp.server.decorators import Route
from raphson_mp.server.dev_reload import observe_changes, restart
from raphson_mp.server.features import FEATURES, Feature
from raphson_mp.server.vars import APP_JINJA_ENV, CLOSE_RESPONSES

_LOGGER = logging.getLogger(__name__)


@dataclass
class RoutesModule:
    name: str
    prefix: str | None
    enabled: Callable[[], bool]


ROUTES_MODULES: list[RoutesModule] = [
    RoutesModule("account", "/account", lambda: not settings.offline_mode),
    RoutesModule("activity_offline", "/activity", lambda: settings.offline_mode),
    RoutesModule("activity", "/activity", lambda: not settings.offline_mode),
    RoutesModule("auth", "/auth", lambda: not settings.offline_mode),
    RoutesModule("control", "/control", lambda: not settings.offline_mode),
    RoutesModule("dav", "/dav", lambda: Feature.WEBDAV in FEATURES and not settings.offline_mode),
    RoutesModule("dislikes", "/dislikes", lambda: not settings.offline_mode),
    RoutesModule("download", "/download", lambda: Feature.DOWNLOADER in FEATURES and not settings.offline_mode),
    RoutesModule("export", "/export", lambda: not settings.offline_mode),
    RoutesModule("files", "/files", lambda: not settings.offline_mode),
    RoutesModule("games", "/games", lambda: Feature.GAMES in FEATURES),
    RoutesModule("info", "/info", lambda: True),
    RoutesModule("lastfm", "/lastfm", lambda: not settings.offline_mode),
    RoutesModule("log", "/log", lambda: True),
    RoutesModule("metrics", "/metrics", lambda: not settings.offline_mode),
    RoutesModule("offline", "/offline", lambda: settings.offline_mode),
    RoutesModule("player", "/player", lambda: True),
    RoutesModule("playlist", "/playlist", lambda: True),
    RoutesModule("playlist_management", "/playlist_management", lambda: not settings.offline_mode),
    RoutesModule("problems", "/problems", lambda: not settings.offline_mode),
    RoutesModule("radio", "/radio", lambda: Feature.RADIO in FEATURES),
    RoutesModule("root", None, lambda: True),
    RoutesModule("share", "/share", lambda: not settings.offline_mode),
    RoutesModule("static", "/static", lambda: True),
    RoutesModule("stats", "/stats", lambda: True),
    RoutesModule("subsonic", "/rest", lambda: Feature.SUBSONIC in FEATURES and not settings.offline_mode),
    RoutesModule("track_offline", "/track", lambda: settings.offline_mode),
    RoutesModule("track", "/track", lambda: not settings.offline_mode),
    RoutesModule("tracks", "/tracks", lambda: True),
    RoutesModule("users", "/users", lambda: not settings.offline_mode),
]


class TaskScheduler:
    MAINTENANCE_INTERVAL: Final = 3600

    # keep strong reference to running tasks
    _tasks: list[asyncio.Task[None]]

    def __init__(self, app: web.Application):
        app.on_startup.append(self.on_startup)
        self._tasks = []

    async def on_startup(self, _app: web.Application):
        if settings.offline_mode:
            from raphson_mp.server import offline_lyrics_migration
            self._tasks.append(asyncio.create_task(offline_lyrics_migration.migrate_task()))
        else:
            from raphson_mp.server import activity, lyrics

            self._tasks.append(asyncio.create_task(self.run_periodically(self.maintenance, self.MAINTENANCE_INTERVAL)))
            self._tasks.append(asyncio.create_task(self.run_periodically(activity.remove_expired_playing, 10)))
            self._tasks.append(asyncio.create_task(self.run_periodically(lyrics.find_task, 60)))
            self._tasks.append(asyncio.create_task(self.run_periodically(blob.generate_missing, 60)))

    @staticmethod
    async def run_periodically(func: Callable[[], Awaitable[None]], interval: int, start_immediately: bool = False):
        if not start_immediately:
            await asyncio.sleep(random.randint(interval // 4, (interval // 4) * 3))
        while True:

            async def func_log_exceptions():
                try:
                    await func()
                except Exception:
                    _LOGGER.error("error in periodic task", exc_info=True)

            await asyncio.gather(asyncio.sleep(interval), func_log_exceptions())

    @staticmethod
    async def maintenance():
        with util.log_duration("maintenance"):
            await asyncio.to_thread(db.optimize)
            await scanner.scan(None)
            await asyncio.to_thread(trash_cleanup)
            await cache.cleanup()
            await auth.prune_old_session_tokens()
            await blob.cleanup()


class Server:
    SHUTDOWN_TIMEOUT: int = 5
    dev: bool
    app: web.Application
    should_restart: bool = False
    cleanup: list[Callable[[], Awaitable[None]]]
    asyncio_debug: bool

    def __init__(self, dev: bool, enable_profiler: bool = False, asyncio_debug: bool = False):
        self.asyncio_debug = asyncio_debug
        self.dev = dev

        middleware_list: list[Middleware] = [
            middlewares.unhandled_error,
            middlewares.csp,
            middlewares.proxy_fix,
            middlewares.auth_error,
        ]
        if enable_profiler:
            middleware_list.append(middlewares.profiler)
        if dev:
            middleware_list.append(middlewares.no_cache)
        if not settings.offline_mode:
            from raphson_mp.routes import metrics

            middleware_list.append(metrics.request_counter)

        self.app = web.Application(
            middlewares=middleware_list,
            client_max_size=1024**3,
        )
        self.cleanup = []
        self.app[CLOSE_RESPONSES] = weakref.WeakSet()

        self.app.on_startup.append(self._startup)
        self.app.on_shutdown.append(self._shutdown)
        self.app.on_cleanup.append(self._cleanup)

        self._setup_jinja()

        self._register_routes()

        TaskScheduler(self.app)

    async def _startup(self, _app: web.Application):
        if self.asyncio_debug:
            asyncio.get_running_loop().set_debug(True)

        if self.dev:
            _LOGGER.info("running in development mode")

            async def on_change():
                self.should_restart = True
                signal.raise_signal(signal.SIGINT)

            asyncio.create_task(observe_changes(on_change))

        httpclient.enable_cached_connector()

    async def _shutdown(self, app: web.Application):
        _LOGGER.info("shutting down, please wait up to %s seconds", self.SHUTDOWN_TIMEOUT)
        _LOGGER.debug("waiting for pending requests to finish")
        for response in app[CLOSE_RESPONSES]:
            _LOGGER.info("force closing: %s", response)
            if isinstance(response, web.WebSocketResponse):
                _LOGGER.info("closing websocket: %s", response)
                await response.close()
            else:
                _LOGGER.info("cancelling request: %s", response)
                if task := response.task:
                    task.cancel()

        _LOGGER.debug("waiting for background tasks to finish")
        await util.await_tasks(self.SHUTDOWN_TIMEOUT)

    async def _cleanup(self, _app: web.Application):
        await httpclient.close()
        for task in self.cleanup:
            await task()

    def _setup_jinja(self):
        jinja_env = jinja2.Environment(
            loader=jinja2.PackageLoader("raphson_mp"),
            autoescape=True,
            enable_async=True,
            auto_reload=self.dev,
            undefined=jinja2.StrictUndefined,
        )
        i18n.install_jinja2_extension(jinja_env)
        self.app[APP_JINJA_ENV] = jinja_env

    def _register_routes(self):
        for module in ROUTES_MODULES:
            if module.enabled():
                _LOGGER.debug("registering routes: %s", module.name)
                self._register_routes_module(module)

    def _register_routes_module(self, module: RoutesModule):
        python_module = importlib.import_module("raphson_mp.routes." + module.name)
        members: list[tuple[str, Route]] = inspect.getmembers_static(
            python_module, lambda member: isinstance(member, Route)
        )
        if module.prefix is None:
            for member in members:
                self.app.add_routes(member[1].routedefs)
        else:
            subapp = web.Application()
            for member in members:
                subapp.add_routes(member[1].routedefs)
            self.app.add_subapp(module.prefix, subapp)

    async def start(self, host: str, port: int):
        _LOGGER.info("starting web server on http://%s:%s", host, port)
        web.run_app
        runner = web.AppRunner(
            self.app,
            access_log=access_logger if settings.access_log else None,
            access_log_format='%a %r %s %Tfs "%{User-Agent}i"',
            handler_cancellation=True,
            shutdown_timeout=self.SHUTDOWN_TIMEOUT,
        )
        await runner.setup()
        site = web.TCPSite(
            runner,
            host=host,
            port=port,
        )
        await site.start()

        # wait forever
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            await runner.cleanup()

            if self.should_restart:
                os.putenv("MUSIC_HAS_RELOADED", "1")
                restart()


def trash_cleanup():
    """Delete trashed files and directories after 30 days."""
    assert settings.music_dir is not None
    for path in settings.music_dir.glob(f"**/{TRASH_PREFIX}*"):
        if path.stat().st_ctime < time.time() - 60 * 60 * 24 * 30:
            _LOGGER.info("permanently deleting: %s", path.as_posix())
            if path.is_file():
                path.unlink()
            else:
                shutil.rmtree(path)
