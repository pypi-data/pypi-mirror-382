import asyncio
import logging
import uuid
from collections.abc import Awaitable, Callable
from io import UnsupportedOperation
from typing import cast

from aiohttp import ClientTimeout, ClientWebSocketResponse, StreamReader, WSMsgType
from aiohttp.client import ClientSession

from raphson_mp.client.playlist import Playlist
from raphson_mp.client.track import DownloadedTrack, Track
from raphson_mp.client.util import get_raphson_logo
from raphson_mp.common.control import ClientCommand, ServerCommand, parse
from raphson_mp.common.music import Album
from raphson_mp.common.track import NEWS_PATH
from raphson_mp.common.typing import FilterResponseDict, PlaylistDict, SearchResponseDict, TrackDict
from raphson_mp.common.util import urlencode

_LOGGER = logging.getLogger(__name__)


class RaphsonMusicClient:
    player_id: str
    session: ClientSession
    control_task: asyncio.Task[None] | None = None
    control_ws: ClientWebSocketResponse | None = None

    def __init__(self):
        self.player_id = str(uuid.uuid4())
        self.session = None  # pyright: ignore[reportAttributeAccessIssue]

    async def setup(self, *, base_url: str, user_agent: str, token: str) -> None:
        self.session = ClientSession(
            base_url=base_url,
            headers={"User-Agent": user_agent, "Authorization": "Bearer " + token},
            timeout=ClientTimeout(connect=5, total=60),
            raise_for_status=True,
        )

    async def close(self) -> None:
        if self.session:
            await self.session.close()

    async def choose_track(self, playlist: Playlist | str) -> Track:
        if isinstance(playlist, Playlist):
            playlist = playlist.name
        async with self.session.post("/playlist/" + urlencode(playlist) + "/choose_track", json={}) as response:
            data = cast(TrackDict, await response.json())
        return Track.from_dict(data)

    async def get_track(self, path: str) -> Track:
        async with self.session.get("/track/" + urlencode(path) + "/info") as response:
            data = cast(TrackDict, await response.json())
        return Track.from_dict(data)

    async def download_news(self) -> DownloadedTrack:
        track = await self.get_track(NEWS_PATH)
        return await track.download(self)

    async def submit_played(self, track_path: str, timestamp: int) -> None:
        async with self.session.post("/activity/played", json={"track": track_path, "timestamp": timestamp}):
            pass

    async def signal_stop(self) -> None:
        async with self.session.post("/activity/stop", data={"id": self.player_id}):
            pass

    async def get_raphson_logo(self) -> bytes:
        return await get_raphson_logo(self.session)

    async def list_tracks_response(self, playlist: str) -> StreamReader:
        response = await self.session.get("/tracks/filter", params={"playlist": playlist})
        return response.content

    async def list_tracks(self, playlist: str | Playlist) -> list[Track]:
        if isinstance(playlist, Playlist):
            playlist = playlist.name
        async with self.session.get("/tracks/filter", params={"playlist": playlist}) as response:
            response_json = cast(FilterResponseDict, await response.json())
        return [Track.from_dict(data) for data in response_json["tracks"]]

    async def playlists(self) -> list[Playlist]:
        async with self.session.get("/playlist/list") as response:
            return [
                Playlist(
                    name=playlist["name"],
                    track_count=playlist["track_count"],
                    favorite=playlist["favorite"],
                    write=playlist["write"],
                )
                for playlist in cast(list[PlaylistDict], await response.json())
            ]

    async def playlist(self, name: str) -> Playlist | None:
        playlists = await self.playlists()
        return next(filter(lambda p: p.name == name, playlists), None)

    async def dislikes(self) -> set[str]:
        async with self.session.get("/dislikes/json") as response:
            json = await response.json()
        return set(json["tracks"])

    async def tags(self) -> set[str]:
        async with self.session.get("/tracks/tags") as response:
            return set(cast(list[str], await response.json()))

    async def search(self, query: str) -> tuple[list[Track], list[Album]]:
        async with self.session.get("/tracks/search", params={"query": query}) as response:
            result = cast(SearchResponseDict, await response.json())
            tracks = [Track.from_dict(track) for track in result["tracks"]]
            albums = [Album.from_dict(album_dict) for album_dict in result["albums"]]
            return tracks, albums

    async def _control_task(self, handler: Callable[[ServerCommand], Awaitable[ClientCommand | None]] | None = None):
        while True:
            _LOGGER.info("connecting to websocket")
            try:
                async with self.session.ws_connect("/control", params={"id": self.player_id}) as ws:
                    self.control_ws = ws
                    async for message in ws:
                        if message.type == WSMsgType.TEXT:
                            if handler is None:
                                continue
                            command = parse(message.data)
                            assert isinstance(command, ServerCommand)
                            try:
                                response = await handler(command)
                                if response:
                                    await ws.send_json(response.data())
                            except Exception:
                                _LOGGER.error("error in websocket message handler", exc_info=True)
                        elif message.type == WSMsgType.ERROR:
                            break
            except Exception:
                _LOGGER.error("error in websocket connection", exc_info=True)
            finally:
                self.control_ws = None

            _LOGGER.info("reconnecting to websocket in 5 seconds")
            await asyncio.sleep(5)

    def control_start(self, handler: Callable[[ServerCommand], Awaitable[ClientCommand | None]] | None = None):
        if self.control_task and not self.control_task.done():
            raise UnsupportedOperation("control channel is already active")

        self.control_task = asyncio.create_task(self._control_task(handler))

    async def control_stop(self):
        if self.control_task:
            self.control_task.cancel()

            try:
                await self.control_task
            except asyncio.CancelledError:
                pass

        self.control_task = None

    async def control_send(self, command: ClientCommand):
        retries = 0
        while not self.control_ws and retries < 1000:
            retries += 1
            await asyncio.sleep(1)

        if not self.control_ws:
            raise UnsupportedOperation("websocket is still not active after waiting 1 second")

        await command.send(self.control_ws)
