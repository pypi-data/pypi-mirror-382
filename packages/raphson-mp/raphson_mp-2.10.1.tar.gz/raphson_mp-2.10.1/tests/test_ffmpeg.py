import asyncio
import itertools
import tempfile
from pathlib import Path
from sqlite3 import Connection

from raphson_mp.client.track import Track
from raphson_mp.common import const
from raphson_mp.common.image import ImageFormat, ImageQuality
from raphson_mp.common.track import AudioFormat
from raphson_mp.server import ffmpeg
from raphson_mp.server.track import FileTrack, from_relpath


async def test_thumbnail():
    image = Path("docs/tyrone_music.jpg").read_bytes()
    options = itertools.product(ImageFormat, ImageQuality, [True, False])
    thumbnails = await asyncio.gather(
        *[ffmpeg.image_thumbnail(image, img_format, img_quality, square) for img_format, img_quality, square in options]
    )
    results = await asyncio.gather(*[ffmpeg.check_image(thumbnail) for thumbnail in thumbnails])
    assert all(results)


async def test_corrupt_image():
    assert await ffmpeg.check_image(b"not an image!") is False


async def test_transcode(track: Track, conn: Connection):
    input_path = from_relpath(track.path)

    # for MP3 format
    server_track = FileTrack(conn, track.path)

    loudness = await ffmpeg.measure_loudness(input_path)
    assert loudness is not None

    async def transcode(audio_format: AudioFormat):
        with tempfile.NamedTemporaryFile() as output_tempfile:
            output_path = Path(output_tempfile.name)
            await ffmpeg.transcode_audio(input_path, loudness, audio_format, output_path, server_track)

    _ = await asyncio.gather(*[transcode(audio_format) for audio_format in AudioFormat])


async def test_probe_corrupt():
    meta = await ffmpeg.probe_metadata(Path("babel.cfg"))
    assert meta is None


async def test_probe_image():
    meta = await ffmpeg.probe_metadata(const.RAPHSON_PNG_PATH)
    assert meta is None


async def test_probe():
    meta = await ffmpeg.probe_metadata(Path("tests/data/test.mp3"))
    assert meta is not None
    assert meta.title == "TestTitle"
    assert meta.artists == ["TestArtist1", "TestArtist2"]
    assert meta.album == "TestAlbum"
    assert meta.album_artist == "TestAlbumArtist"
    assert meta.tags == ["TestGenre1", "TestGenre2"]
    assert meta.track_number == 24
    assert meta.year == 2000
    assert meta.duration == 7
