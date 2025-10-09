import hmac
import logging
import time
from sqlite3 import Connection
from weakref import WeakSet, WeakValueDictionary

from aiohttp import WSMsgType, web

from raphson_mp.common import eventbus
from raphson_mp.common.control import (
    ClientPlaying,
    ClientRelayCommand,
    ClientSubscribe,
    ClientToken,
    ServerFileChange,
    ServerPlayed,
    ServerPlayingStopped,
    Topic,
    parse,
    send,
)
from raphson_mp.server import activity, events
from raphson_mp.server.auth import User
from raphson_mp.server.decorators import route
from raphson_mp.server.vars import CLOSE_RESPONSES

_LOGGER = logging.getLogger(__name__)

_BY_ID: WeakValueDictionary[str, web.WebSocketResponse] = WeakValueDictionary()
_SUB_PLAYING: WeakSet[web.WebSocketResponse] = WeakSet()
_SUB_FILES: WeakSet[web.WebSocketResponse] = WeakSet()

received_message_counter: int = 0


@route("", method="GET")
async def websocket(request: web.Request, _conn: Connection, user: User):
    player_id = request.query.get("id")

    if player_id is None:
        raise web.HTTPBadRequest(reason="missing id")

    # If cookies are set, they may have been used to log in and CSRF is possible. In this case,
    # the client must first provide CSRF token before it is trusted.
    trusted = "Cookie" not in request.headers

    ws = web.WebSocketResponse()

    _BY_ID[player_id] = ws
    request.config_dict[CLOSE_RESPONSES].add(ws)

    _LOGGER.info("client connected: %s", player_id)

    await ws.prepare(request)

    async for message in ws:
        if message.type == WSMsgType.TEXT:
            try:
                command = parse(message.data)
                _LOGGER.debug("received message %s", command.__class__.__name__)
            except Exception:
                _LOGGER.warning("failed to parse message %s", message.data)
                continue

            global received_message_counter
            received_message_counter += 1

            if not trusted:
                if isinstance(command, ClientToken):
                    if hmac.compare_digest(user.csrf, command.csrf):
                        trusted = True
                    else:
                        _LOGGER.warning("invalid CSRF token")
                else:
                    _LOGGER.warning("ignoring command, client needs to send CSRF token first")
                continue

            if isinstance(command, ClientPlaying):
                await activity.set_now_playing(
                    user,
                    player_id,
                    40,
                    command,
                )
            elif isinstance(command, ClientSubscribe):
                if command.topic == Topic.ACTIVITY:
                    _LOGGER.warning("received ClientSubscribe with deprecated topic 'activity'")
                    _SUB_PLAYING.add(ws)
                    _SUB_FILES.add(ws)

                    # send current data to the client immediately
                    await send(ws, [playing.control_command() for playing in activity.now_playing()])
                elif command.topic == Topic.PLAYING:
                    _SUB_PLAYING.add(ws)
                    # send current data to the client immediately
                    await send(ws, [playing.control_command() for playing in activity.now_playing()])
                elif command.topic == Topic.FILES:
                    _SUB_FILES.add(ws)
            elif isinstance(command, ClientRelayCommand):
                target = _BY_ID.get(command.player_id)
                if target is not None:
                    await send(target, command.server_command())
                else:
                    _LOGGER.warning("unknown player id")
            else:
                _LOGGER.warning("ignoring unsupported command: %s", command)

    _LOGGER.info("client disconnected: %s", player_id)

    return ws


async def broadcast_playing(event: events.NowPlayingEvent) -> None:
    await send(_SUB_PLAYING, event.now_playing.control_command())


async def broadcast_stop_playing(event: events.StoppedPlayingEvent) -> None:
    await send(_SUB_PLAYING, ServerPlayingStopped(player_id=event.player_id))


async def broadcast_history(event: events.TrackPlayedEvent):
    await send(
        _SUB_PLAYING,
        ServerPlayed(
            username=event.user.nickname if event.user.nickname else event.user.username,
            played_time=event.timestamp,
            track=event.track.to_dict(),
        ),
    )


async def broadcast_file_change(event: events.FileChangeEvent):
    username = None
    if event.user:
        username = event.user.nickname if event.user.nickname else event.user.username
    await send(
        _SUB_FILES,
        ServerFileChange(
            change_time=int(time.time()), action=event.action.value, track=event.track, username=username
        ),
    )


eventbus.subscribe(events.NowPlayingEvent, broadcast_playing)
eventbus.subscribe(events.StoppedPlayingEvent, broadcast_stop_playing)
eventbus.subscribe(events.TrackPlayedEvent, broadcast_history)
eventbus.subscribe(events.FileChangeEvent, broadcast_file_change)
