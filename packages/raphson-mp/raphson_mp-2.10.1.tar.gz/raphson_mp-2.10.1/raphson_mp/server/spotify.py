import logging
import time
from collections.abc import AsyncIterator
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass
from typing import TypedDict, cast

import aiohttp

from raphson_mp.common import httpclient, util
from raphson_mp.server import settings

if settings.offline_mode:
    # Module must not be imported to ensure no data is ever downloaded in offline mode.
    raise RuntimeError("Cannot use spotify in offline mode")


log = logging.getLogger(__name__)


class _TokenResponseDict(TypedDict):
    access_token: str
    expires_in: int


@dataclass
class Track:
    title: str
    artists: list[str]

    @property
    def display(self) -> str:
        return ", ".join(self.artists) + " - " + self.title


class SpotifyClient:
    _api_id: str
    _api_secret: str
    _access_token: str | None = None
    _access_token_expiry: int = 0

    def __init__(self, api_id: str, api_secret: str):
        self._api_id = api_id
        self._api_secret = api_secret

    async def get_access_token(self) -> str:
        if self._access_token is not None:
            if self._access_token_expiry > int(time.time()):
                return self._access_token

        async with httpclient.session() as session:
            async with session.post(
                "https://accounts.spotify.com/api/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self._api_id,
                    "client_secret": self._api_secret,
                },
            ) as response:
                json = cast(_TokenResponseDict, await response.json())

        access_token: str = json["access_token"]
        self._access_token = access_token
        self._access_token_expiry = int(time.time()) + json["expires_in"]
        return access_token

    async def _session(self) -> AbstractAsyncContextManager[aiohttp.ClientSession]:
        return httpclient.session(
            headers={
                "Authorization": "Bearer " + await self.get_access_token(),
            },
        )

    async def get_playlist(self, playlist_id: str) -> AsyncIterator[Track]:
        url = "https://api.spotify.com/v1/playlists/" + util.urlencode(playlist_id) + "/tracks"

        async with await self._session() as session:
            while url:
                log.info("making request to: %s", url)

                async with session.get(url, params={"fields": "next,items(track(name,artists(name)))"}) as response:
                    json = await response.json()

                for track in json["items"]:
                    title = track["track"]["name"]
                    artists = [artist["name"] for artist in track["track"]["artists"]]
                    yield Track(title, artists)

                url = json["next"]

    async def get_artist_image(self, name: str):
        async with await self._session() as session:
            async with session.get(
                "https://api.spotify.com/v1/search",
                params={"q": "artist:" + name, "type": "artist", "market": "NL", "limit": 1},
            ) as response:
                json = await response.json()
                items = json["artists"]["items"]
                if not items:
                    return None
                artist = items[0]
                images = artist["images"]
                if not images:
                    return None
                image_url = images[0]["url"]

        log.debug("downloading image: %s", image_url)

        async with httpclient.session() as session:
            async with session.get(image_url) as response:
                return await response.content.read()


_cached_client: SpotifyClient | None = None


def client() -> SpotifyClient | None:
    global _cached_client
    if _cached_client:
        return _cached_client

    if settings.spotify_api_id and settings.spotify_api_secret:
        return (_cached_client := SpotifyClient(settings.spotify_api_id, settings.spotify_api_secret))
    else:
        return None
