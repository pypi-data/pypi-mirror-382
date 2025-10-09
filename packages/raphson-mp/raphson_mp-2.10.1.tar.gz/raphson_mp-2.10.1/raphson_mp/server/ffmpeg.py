from __future__ import annotations

import asyncio
import json
import logging
import os
import tempfile
from dataclasses import dataclass, field
from json import JSONDecodeError
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import TypedDict

from raphson_mp.common import metadata, process
from raphson_mp.common.image import ImageFormat, ImageQuality
from raphson_mp.common.track import AudioFormat
from raphson_mp.server import settings, track

_LOGGER = logging.getLogger(__name__)
_FFMPEG = "ffmpeg"
_LOUDNORM_I = -14  # must not be changed, or tracks will have inconsistent loudness!
_LOUDNORM_LRA = 20
_LOUDNORM_TP = -2


def common_opts():
    return [
        _FFMPEG,
        "-hide_banner",
        "-nostats",
    ]


async def image_thumbnail(image: bytes, img_format: ImageFormat, img_quality: ImageQuality, square: bool) -> bytes:
    size = img_quality.resolution

    if square:
        thumb_filter = f"scale={size}:{size}:force_original_aspect_ratio=increase,crop={size}:{size}"
    else:
        thumb_filter = f"scale={size}:{size}:force_original_aspect_ratio=decrease"

    if img_format is ImageFormat.WEBP:
        format_options = ["-pix_fmt", "yuv420p", "-f", "webp"]
    elif img_format is ImageFormat.JPEG:
        format_options = ["-pix_fmt", "yuvj420p", "-f", "mjpeg"]

    with NamedTemporaryFile() as temp_input, NamedTemporaryFile() as temp_output:
        await asyncio.to_thread(temp_input.write, image)
        await asyncio.to_thread(temp_input.flush)
        await process.run(
            [
                *common_opts(),
                "-loglevel",
                settings.ffmpeg_log_level,
                "-y",  # overwrite the temp file, it already exists
                "-i",
                temp_input.name,
                "-filter",
                thumb_filter,
                *format_options,
                temp_output.name,
            ],
            ro_mounts=[temp_input.name],
            rw_mounts=[temp_output.name],
        )
        return await asyncio.to_thread(temp_output.read)


async def check_image(image_data: bytes):
    """Check if the provided image data is valid (not corrupt)"""
    try:
        await image_thumbnail(image_data, ImageFormat.JPEG, ImageQuality.LOW, False)
        return True
    except process.ProcessReturnCodeError:
        return False


class LoudnessParams(TypedDict):
    input_i: float
    input_tp: float
    input_lra: float
    input_thresh: float
    target_offset: float
    normalization_type: str


def _parse_loudness(stderr: bytes) -> LoudnessParams:
    # Manually find the start of loudnorm info json
    try:
        meas_out = stderr.decode(encoding="utf-8")
    except UnicodeDecodeError:
        meas_out = stderr.decode(encoding="latin-1")
    start = meas_out.rindex("Parsed_loudnorm_0") + 37
    end = start + meas_out[start:].index("}") + 1
    json_text = meas_out[start:end]
    try:
        meas_json = json.loads(json_text)
    except JSONDecodeError as ex:
        _LOGGER.error("invalid json: %s", json_text)
        _LOGGER.error("original output: %s", meas_out)
        raise ex

    _LOGGER.debug("loudness data: %s", meas_json)

    return {
        "input_i": float(meas_json["input_i"]),
        "input_tp": float(meas_json["input_tp"]),
        "input_lra": float(meas_json["input_lra"]),
        "input_thresh": float(meas_json["input_thresh"]),
        "target_offset": float(meas_json["target_offset"]),
        "normalization_type": meas_json["normalization_type"],
    }


async def measure_loudness(measure_path: Path) -> LoudnessParams:
    # First phase of 2-phase loudness normalization
    # https://k.ylo.ph/2016/04/04/loudnorm.html

    _LOGGER.info("measuring loudness: %s", measure_path.as_posix())
    # Annoyingly, loudnorm outputs to stderr instead of stdout. Disabling logging also
    # hides the loudnorm output, so we must parse loudnorm from the output.
    _stdout, stderr = await process.run(
        [
            *common_opts(),
            "-i",
            measure_path.as_posix(),
            "-map",
            "0:a",
            "-filter:a",
            "loudnorm=print_format=json",
            "-f",
            "null",
            "-",
        ],
        ro_mounts=[(measure_path.as_posix())],
    )

    return _parse_loudness(stderr)


def _get_loudnorm_filter(measured_loudness: LoudnessParams):

    if not (-99 < measured_loudness["input_i"] < 0):
        _LOGGER.warning(
            "Integrated loudness value is invalid: %s. The track is probably corrupt, containing out "
            + "of range values. Using dynamic single-pass loudnorm filter.",
            measured_loudness["input_i"],
        )
        return f"loudnorm=print_format=json:I={_LOUDNORM_I}:LRA={_LOUDNORM_LRA}:TP={_LOUDNORM_TP}"

    # max safe loudness idea based on: https://github.com/slhck/ffmpeg-normalize/pull/273
    max_safe_loudness = measured_loudness["input_i"] - measured_loudness["input_tp"] + _LOUDNORM_TP - 0.1
    if max_safe_loudness < _LOUDNORM_I:
        _LOGGER.info(
            "using lower loudness target %.1f (instead of %s) to keep peaks below max TP (%s)",
            max_safe_loudness,
            _LOUDNORM_I,
            _LOUDNORM_TP,
        )
        target_loudness = max_safe_loudness
    else:
        target_loudness = _LOUDNORM_I

    return (
        f"loudnorm=print_format=json:"
        + f"I={target_loudness:.2f}:"
        + f"LRA={_LOUDNORM_LRA}:"
        + f"TP={_LOUDNORM_TP}:"
        + f"measured_I={measured_loudness['input_i']}:"
        + f"measured_TP={measured_loudness['input_tp']}:"
        + f"measured_LRA={measured_loudness['input_lra']}:"
        + f"measured_thresh={measured_loudness['input_thresh']}:"
        + f"offset={measured_loudness['target_offset']}:"
        + "linear=true"
    )


async def transcode_audio(
    input_path: Path,
    input_loudness: LoudnessParams,
    output_format: AudioFormat,
    output_path: Path,
    track: track.FileTrack | None = None,
):
    _LOGGER.info("transcoding audio: %s (input loudness: %s)", input_path.as_posix(), input_loudness["input_i"])

    ro_mounts = [input_path.as_posix()]
    rw_mounts = [output_path.as_posix()]

    if output_format in {AudioFormat.WEBM_OPUS_HIGH, AudioFormat.WEBM_OPUS_LOW}:
        input_options = [
            "-map",
            "0:a",  # only keep audio
            "-map_metadata",
            "-1",  # discard metadata
        ]
        bit_rate = "128k" if output_format == AudioFormat.WEBM_OPUS_HIGH else "48k"
        audio_options = [
            "-f",
            "webm",
            "-c:a",
            "libopus",
            "-b:a",
            bit_rate,
            "-vbr",
            "on",
            # Higher frame duration offers better compression at the cost of latency
            "-frame_duration",
            "60",
            "-vn",
        ]  # remove video track (and album covers)
    elif output_format is AudioFormat.MP3_WITH_METADATA:
        assert track, "track must be provided when transcoding to MP3"

        cover = await track.get_cover(False, ImageQuality.HIGH, img_format=ImageFormat.JPEG)
        # Write cover to temp file so ffmpeg can read it
        cover_fd, cover_path = tempfile.mkstemp()
        os.write(cover_fd, cover)
        os.close(cover_fd)

        ro_mounts.append(cover_path)

        # https://trac.ffmpeg.org/wiki/Encode/MP3
        input_options = [
            "-i",
            cover_path,  # add album cover
            "-map",
            "0:a",  # include audio stream from first input
            "-map",
            "1:0",  # include first stream from second input
            "-id3v2_version",
            "3",
            "-map_metadata",
            "-1",  # discard original metadata
            "-metadata:s:v",
            "title=Album cover",
            "-metadata:s:v",
            "comment=Cover (front)",
            *track.get_ffmpeg_options(),
        ]  # set new metadata

        audio_options = [
            "-f",
            "mp3",
            "-c:a",
            "libmp3lame",
            "-c:v",
            "copy",  # Leave cover as JPEG, don't re-encode as PNG
            "-q:a",
            "2",
        ]  # VBR 190kbps
    else:
        raise ValueError(output_format)

    _stdout, stderr = await process.run(
        [
            *common_opts(),
            "-y",  # overwriting file is required, because the created temp file already exists
            "-i",
            input_path.as_posix(),
            *input_options,
            *audio_options,
            "-t",
            str(settings.track_max_duration_seconds),
            "-ac",
            "2",
            "-filter:a",
            _get_loudnorm_filter(input_loudness),
            output_path.as_posix(),
        ],
        ro_mounts=ro_mounts,
        rw_mounts=rw_mounts,
    )

    loudness2 = _parse_loudness(stderr)

    if loudness2["normalization_type"] != "linear":
        _LOGGER.warning("dynamic normalization was used for: %s", input_path.as_posix())

    if output_format is AudioFormat.MP3_WITH_METADATA:
        os.unlink(cover_path)  # pyright: ignore[reportPossiblyUnboundVariable]


@dataclass
class Metadata:
    duration: int
    artists: list[str] = field(default_factory=list)
    album: str | None = None
    title: str | None = None
    year: int | None = None
    album_artist: str | None = None
    track_number: int | None = None
    tags: list[str] = field(default_factory=list)
    lyrics: str | None = None
    video: str | None = None


async def probe_metadata(path: Path) -> Metadata | None:
    """
    Create cdictionary of track metadata, to be used as SQL query parameters
    """
    try:
        stdout, _stderr = await process.run(
            ["ffprobe", "-show_streams", "-show_format", "-print_format", "json", path.as_posix()],
            ro_mounts=[path.as_posix()],
        )
    except process.ProcessReturnCodeError:
        _LOGGER.warning("error scanning track %s, is it corrupt?", path)
        return None

    data = json.loads(stdout.decode())

    if "duration" not in data["format"]:
        # static image
        return None

    duration = int(float(data["format"]["duration"]))
    meta = Metadata(duration)

    meta_tags: list[tuple[str, str]] = []

    for stream in data["streams"]:
        if stream["codec_type"] == "audio":
            if "tags" in stream:
                meta_tags.extend(stream["tags"].items())

        if stream["codec_type"] == "video":
            if stream["codec_name"] == "vp9":
                meta.video = "vp9"
            elif stream["codec_name"] == "h264":
                meta.video = "h264"

    if "tags" in data["format"]:
        meta_tags.extend(data["format"]["tags"].items())

    for name, value in meta_tags:
        # sometimes ffprobe returns tags in uppercase
        name = name.lower()

        if value.strip() == "":
            _LOGGER.info('ignoring empty value: %s', name)
            continue

        if metadata.has_advertisement(value):
            _LOGGER.info("ignoring advertisement: %s = %s", name, value)
            continue

        # replace weird quotes by normal quotes
        value = value.replace("’", "'").replace("`", "'")

        if name == "album":
            meta.album = value

        if name == "artist":
            meta.artists = metadata.split_meta_list(value)

        if name == "title":
            meta.title = metadata.strip_keywords(value).strip()

        if name == "date":
            try:
                meta.year = int(value[:4])
            except ValueError:
                _LOGGER.warning("Invalid year '%s' in file '%s'", value, path.resolve().as_posix())

        if name == "album_artist":
            meta.album_artist = value

        if name == "track":
            try:
                meta.track_number = int(value.split("/")[0])
            except ValueError:
                _LOGGER.warning(
                    "Invalid track number '%s' in file '%s'",
                    value,
                    path.resolve().as_posix(),
                )

        if name == "genre":
            meta.tags = metadata.split_meta_list(value)

        if name == "lyrics":
            meta.lyrics = value

        # Allow other lyrics tags, but only if no other lyrics are available
        if name in metadata.ALTERNATE_LYRICS_TAGS and meta.lyrics is None:
            meta.lyrics = value

    return meta
