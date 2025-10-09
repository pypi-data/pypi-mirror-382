from aiohttp.client import ClientSession

from raphson_mp.common.util import urlencode


class SharedTrack:
    share_code: str
    track_code: str
    _session: ClientSession

    def __init__(self, share_code: str, track_code: str, session: ClientSession):
        self.share_code = share_code
        self.track_code = track_code
        self._session = session

    @property
    def base_url(self) -> str:
        return "/share/" + urlencode(self.share_code) + "/" + urlencode(self.track_code)

    async def audio(self) -> bytes:
        async with self._session.get(self.base_url + "/audio") as response:
            return await response.content.read()

    async def cover(self) -> bytes:
        async with self._session.get(self.base_url + "/cover") as response:
            return await response.content.read()


class Share:
    share_code: str
    _session: ClientSession

    def __init__(self, share_code: str, session: ClientSession):
        self.share_code = share_code
        self._session = session

    async def tracks(self) -> list[SharedTrack]:
        async with self._session.get("/share/" + urlencode(self.share_code) + "/json") as response:
            return [SharedTrack(self.share_code, track_code, self._session) for track_code in await response.json()]
