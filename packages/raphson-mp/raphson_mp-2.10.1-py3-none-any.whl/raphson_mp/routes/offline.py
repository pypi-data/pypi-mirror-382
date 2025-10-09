import asyncio
import logging
from collections.abc import AsyncIterator
from dataclasses import dataclass
from sqlite3 import Connection
from typing import cast

from aiohttp import web

from raphson_mp.common import metadata
from raphson_mp.server import db, offline_sync
from raphson_mp.server.auth import User
from raphson_mp.server.decorators import route
from raphson_mp.server.offline_sync import OfflineSync, WebResponseProgress
from raphson_mp.server.response import template
from raphson_mp.server.vars import CLOSE_RESPONSES

_LOGGER = logging.getLogger(__name__)


@dataclass
class SyncState:
    _sync: OfflineSync | None = None
    _sync_task: asyncio.Task[None] | None = None

    @property
    def active(self):
        return self._sync_task is not None and not self._sync_task.done()

    @property
    def progress(self):
        if self._sync is None:
            raise ValueError()
        return cast(WebResponseProgress, self._sync.progress)

    def start_new(self):
        self._sync = OfflineSync(WebResponseProgress(), 0)
        self._sync_task = asyncio.create_task(self._sync.run())

    def cancel(self):
        if self._sync_task:
            self._sync_task.cancel()


_STATE = SyncState()


@route("/sync")
async def route_sync(_request: web.Request, _conn: Connection, _user: User):
    with db.OFFLINE.connect() as offline:
        row = offline.execute("SELECT base_url, token FROM settings").fetchone()
        server, token = row if row else ("", "")

        rows = offline.execute("SELECT name FROM playlists")
        playlists = metadata.join_meta_list([row[0] for row in rows])

    return await template("offline_sync.jinja2", server=server, token=token, playlists=playlists)


@route("/settings", method="POST")
async def route_settings(request: web.Request, _conn: Connection, _user: User):
    form = await request.post()
    server = cast(str, form["server"])
    token = cast(str, form["token"])
    playlists = metadata.split_meta_list(cast(str, form["playlists"]))

    offline_sync.change_settings(server, token)
    await offline_sync.change_playlists(playlists)

    raise web.HTTPSeeOther("/offline/sync")


@route("/stop", method="POST")
async def route_stop(_request: web.Request, _conn: Connection, _user: User) -> web.Response:
    _STATE.cancel()
    raise web.HTTPNoContent()


@route("/start", method="POST")
async def route_start(_request: web.Request, _conn: Connection, _user: User) -> web.Response:
    if _STATE.active:
        raise web.HTTPBadRequest(reason="sync task is already running")

    _STATE.start_new()

    raise web.HTTPNoContent()


@route("/monitor")
async def route_monitor(request: web.Request, _conn: Connection, _user: User) -> web.Response:
    async def generator() -> AsyncIterator[bytes]:
        while True:
            if _STATE.active:
                yield b"running\n"
                async for entry in _STATE.progress.response_bytes():
                    yield entry
            yield b"stopped\n"
            await asyncio.sleep(0.1)

    response = web.Response(body=generator(), content_type="text/plain")
    request.config_dict[CLOSE_RESPONSES].add(response)
    return response
