import asyncio
import tempfile
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Self

from aiohttp import web
from typing_extensions import override

from raphson_mp.common import const, httpclient
from raphson_mp.common.image import ImageFormat, ImageQuality
from raphson_mp.common.track import NEWS_PATH, AudioFormat, VirtualTrackUnavailableError
from raphson_mp.server import ffmpeg, settings
from raphson_mp.server.track import Track

if settings.offline_mode:
    # Module must not be imported to ensure no data is ever downloaded in offline mode.
    raise RuntimeError("Cannot use virtual tracks in offline mode")


class VirtualTrack(Track, ABC):
    def __init__(self, path: str, timestamp: int, duration: int, title: str):
        super().__init__(
            path=path,
            mtime=timestamp,
            ctime=timestamp,
            duration=duration,
            title=title,
            album=None,
            album_artist=None,
            year=None,
            track_number=None,
            video=None,
            lyrics=None,
            artists=[],
            tags=[],
        )

    @override
    async def get_cover(self, meme: bool, img_quality: ImageQuality, img_format: ImageFormat) -> bytes:
        return const.RAPHSON_PNG_PATH.read_bytes()

    @classmethod
    @abstractmethod
    async def get_instance(cls, args: list[str]) -> Self: ...

    @abstractmethod
    async def get_audio(self, audio_format: AudioFormat) -> web.StreamResponse: ...


class NewsTrack(VirtualTrack):
    wav_audio: bytes

    def __init__(self, wav_audio: bytes, timestamp: int, duration: int, title: str):
        super().__init__(NEWS_PATH, timestamp, duration, title)
        self.wav_audio = wav_audio

    @override
    async def get_audio(self, audio_format: AudioFormat) -> web.StreamResponse:
        with tempfile.NamedTemporaryFile() as wav_temp, tempfile.NamedTemporaryFile() as out_temp:
            wav_path = Path(wav_temp.name)
            out_path = Path(out_temp.name)

            await asyncio.to_thread(wav_path.write_bytes, self.wav_audio)
            loudness = await ffmpeg.measure_loudness(wav_path)
            await ffmpeg.transcode_audio(wav_path, loudness, audio_format, out_path)
            audio = await asyncio.to_thread(out_path.read_bytes)

        return web.Response(body=audio)

    @override
    @classmethod
    async def get_instance(cls, args: list[str]):
        assert len(args) == 0

        if not settings.news_server:
            raise VirtualTrackUnavailableError()

        # Download wave audio to temp file
        with tempfile.NamedTemporaryFile() as temp_file:
            async with httpclient.session(settings.news_server) as session:
                async with session.get("/news.wav", raise_for_status=False) as response:
                    if response.status == 503:
                        raise VirtualTrackUnavailableError()

                    response.raise_for_status()

                    title = response.headers["X-Name"]

                    while chunk := await response.content.read(1024 * 1024):
                        await asyncio.to_thread(temp_file.write, chunk)

            meta = await ffmpeg.probe_metadata(Path(temp_file.name))
            assert meta
            temp_file.seek(0)
            audio_bytes = await asyncio.to_thread(temp_file.read)

        return cls(audio_bytes, int(time.time()), meta.duration, title)


VIRTUAL_TRACK_TYPES: dict[str, type[VirtualTrack]] = {"news": NewsTrack}
