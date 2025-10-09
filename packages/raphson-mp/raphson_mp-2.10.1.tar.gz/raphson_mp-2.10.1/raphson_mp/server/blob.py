from __future__ import annotations

import asyncio
import base64
import logging
import random
import shutil
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import cast
from weakref import WeakValueDictionary

from aiohttp.web import FileResponse
from typing_extensions import override

from raphson_mp.common import process
from raphson_mp.common.track import AudioFormat
from raphson_mp.server import db, ffmpeg, settings
from raphson_mp.server.track import FileTrack

_LOGGER = logging.getLogger(__name__)
LOCKS: WeakValueDictionary[str, asyncio.Lock] = WeakValueDictionary()


def _new_blob_id() -> str:
    return base64.urlsafe_b64encode(random.randbytes(16)).decode().rstrip("=")


def _blob_path(blob_id: str) -> Path:
    blob_dir = settings.blob_dir or Path(settings.data_dir, "blob")
    return Path(blob_dir, blob_id[:2], blob_id[2:])


class Blob(ABC):
    track: FileTrack
    blobtype: str
    content_type: str

    def __init__(self, track: FileTrack, blobtype: str, content_type: str):
        self.track = track
        self.blobtype = blobtype
        self.content_type = content_type

    async def get(self) -> Path:
        lock_key = self.track.path + self.blobtype
        lock = LOCKS.get(lock_key)
        if not lock:
            LOCKS[lock_key] = lock = asyncio.Lock()

        async with lock:
            with db.MUSIC.connect() as conn:
                row = conn.execute(
                    "SELECT id FROM blob WHERE track = ? AND blobtype = ?", (self.track.path, self.blobtype)
                ).fetchone()
                if row:
                    (blob_id,) = cast(tuple[str], row)
                    _LOGGER.debug("returning existing blob: %s", blob_id)
                    path = _blob_path(blob_id)
                    if await asyncio.to_thread(path.is_file):
                        return path
                    else:
                        _LOGGER.warning("blob exists in database but not on disk: %s", blob_id)
                        conn.execute(
                            "DELETE FROM blob WHERE track = ? AND blobtype = ?", (self.track.path, self.blobtype)
                        )

            # blob is not stored on disk and needs to be generated

            async def shielded():
                blob_id = _new_blob_id()
                _LOGGER.debug("storing new blob: %s", blob_id)
                path = _blob_path(blob_id)
                await asyncio.to_thread(path.parent.mkdir, parents=True, exist_ok=True)
                await asyncio.to_thread(path.touch)  # file must exist to be able to bind mount it into the sandbox
                await self.produce(path)
                now = int(time.time())

                with db.MUSIC.connect() as conn:
                    conn.execute("INSERT INTO blob VALUES (?, ?, ?, ?)", (blob_id, self.blobtype, self.track.path, now))
                return path

            return await asyncio.shield(shielded())

    async def response(self):
        return FileResponse(await self.get(), headers={"Content-Type": self.content_type})

    @abstractmethod
    async def produce(self, output_path: Path) -> None: ...

    @classmethod
    @abstractmethod
    def missing(cls) -> Blob | None: ...


class AudioBlob(Blob):
    audio_format: AudioFormat

    def __init__(self, track: FileTrack, audio_format: AudioFormat):
        super().__init__(track, "audio_" + audio_format.value, audio_format.content_type)
        self.audio_format = audio_format

    @override
    async def produce(self, output_path: Path):
        with db.MUSIC.connect() as conn:
            loudness = await self.track.get_loudness(conn)
        await ffmpeg.transcode_audio(self.track.filepath, loudness, self.audio_format, output_path, self.track)

    @override
    @classmethod
    def missing(cls) -> Blob | None:
        with db.MUSIC.connect() as conn:
            for audio_format in AudioFormat:
                blobtype = "audio_" + audio_format.value
                row = conn.execute(
                    "SELECT path FROM track WHERE NOT EXISTS(SELECT * FROM blob WHERE track = path AND blobtype = ?) LIMIT 1",
                    (blobtype,),
                ).fetchone()
                if row is None:
                    continue
                track = FileTrack(conn, row[0])
                return AudioBlob(track, audio_format)
        return None


class VideoBlob(Blob):
    ffmpeg_output_format: str

    def __init__(self, track: FileTrack):
        if track.video == "vp9":
            self.ffmpeg_output_format = "webm"
            output_content_type = "video/webm"
        elif track.video == "h264":
            self.ffmpeg_output_format = "mp4"
            output_content_type = "video/mp4"
        else:
            raise ValueError("file has no suitable video stream")

        super().__init__(track, "video", output_content_type)

    @override
    async def produce(self, output_path: Path):
        input_path = self.track.filepath
        await process.run(
            [
                *ffmpeg.common_opts(),
                "-y",
                "-i",
                input_path.as_posix(),
                "-c:v",
                "copy",
                "-map",
                "0:v",
                "-f",
                self.ffmpeg_output_format,
                output_path.as_posix(),
            ],
            ro_mounts=[input_path.as_posix()],
            rw_mounts=[output_path.as_posix()],
        )

    @override
    @classmethod
    def missing(cls) -> Blob | None:
        with db.MUSIC.connect() as conn:
            row = conn.execute(
                "SELECT path FROM track WHERE video IS NOT NULL AND NOT EXISTS(SELECT * FROM blob WHERE track = path AND blobtype = 'video') LIMIT 1"
            ).fetchone()
            if row is not None:
                return VideoBlob(FileTrack(conn, row[0]))


BLOB_TYPES: list[type[Blob]] = [AudioBlob, VideoBlob]


async def cleanup():
    with db.MUSIC.connect() as conn:
        to_delete = [cast(str, row[0]) for row in conn.execute("SELECT id FROM blob WHERE track IS NULL")]
        for blob_id in to_delete:
            try:
                _LOGGER.debug("delete blob: %s", blob_id)
                await asyncio.to_thread(_blob_path(blob_id).unlink)
            except FileNotFoundError:
                _LOGGER.warning("blob was already missing from disk: %s", blob_id)
            finally:
                conn.execute("DELETE FROM blob WHERE id = ?", (blob_id,))
        _LOGGER.info("deleted %s blobs", len(to_delete))


async def generate_missing():
    for blob_type in BLOB_TYPES:
        while (blob := blob_type.missing()) is not None:
            _total, _used, free = shutil.disk_usage(_blob_path(""))

            if free < 5 * 1024**3:
                _LOGGER.info("not generating missing blobs, free disk space is low")
                return

            _LOGGER.info("generating missing blob: %s %s", blob.track.path, blob.blobtype)
            await blob.get()
