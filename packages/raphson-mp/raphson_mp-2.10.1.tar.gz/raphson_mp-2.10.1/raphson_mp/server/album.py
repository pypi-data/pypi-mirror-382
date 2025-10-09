import asyncio
import logging
import random

from raphson_mp.common import const, image, process
from raphson_mp.server import bing, cache, ffmpeg, musicbrainz, reddit

_LOGGER = logging.getLogger(__name__)


async def _get_cover_data(artist: str | None, album: str, meme: bool):
    _LOGGER.debug("find cover for artist=%s album=%s", artist, album)

    if meme:
        if random.random() > 0.5:
            if image_bytes := await reddit.get_image(album):
                _LOGGER.debug("returning reddit meme for artist=%s album=%s", artist, album)
                return cache.CacheData(image_bytes, cache.MONTH)

        if image_bytes := await bing.image_search(album + " meme"):
            _LOGGER.debug("returning bing meme for artist=%s album=%s", artist, album)
            return cache.CacheData(image_bytes, cache.MONTH)

        _LOGGER.debug("no meme found for artist=%s album=%s, try finding regular cover", artist, album)

    # Try MusicBrainz first
    if artist:
        if image_bytes := await musicbrainz.get_cover(artist, album):
            _LOGGER.debug("returning musicbrainz cover for artist=%s album=%s", artist, album)
            return cache.CacheData(image_bytes, cache.HALFYEAR)

    if artist:
        query = artist + " - " + album
    else:
        query = album + " album cover art"

    # Otherwise try bing
    if image_bytes := await bing.image_search(query):
        _LOGGER.debug("returning bing cover for artist=%s album=%s query=%s", artist, album, query)
        return cache.CacheData(image_bytes, cache.MONTH)

    _LOGGER.debug("returning fallback raphson cover for artist=%s album=%s", artist, album)
    return cache.CacheData(const.RAPHSON_PNG_PATH.read_bytes(), cache.WEEK)


async def _get_cover(artist: str | None, album: str, meme: bool) -> bytes:
    cache_key = f"cover{artist}{album}{meme}"
    return await cache.retrieve_or_store(cache_key, _get_cover_data, artist, album, meme)


async def _get_cover_thumbnail(
    artist: str | None,
    album: str,
    meme: bool,
    img_quality: image.ImageQuality,
    img_format: image.ImageFormat,
) -> cache.CacheData:
    original_bytes = await _get_cover(artist, album, meme)

    _LOGGER.debug(
        "transcoding cover to a thumbnail for artist=%s album=%s meme=%s img_quality=%s img_format=%s",
        artist,
        album,
        meme,
        img_quality,
        img_format,
    )

    try:
        thumbnail = await ffmpeg.image_thumbnail(
            original_bytes,
            img_format,
            img_quality,
            square=not meme,
        )
    except process.ProcessReturnCodeError:
        _LOGGER.warning("failed to generate thumbnail, is the image corrupt? artist=%s album=%s", artist, album)
        thumbnail = await asyncio.to_thread(const.RAPHSON_PNG_PATH.read_bytes)

    return cache.CacheData(thumbnail, cache.MONTH)


async def get_cover_thumbnail(
    artist: str | None, album: str, meme: bool, img_quality: image.ImageQuality, img_format: image.ImageFormat
):
    cache_key = f"coverthumb{artist}{album}{meme}{img_quality.value}{img_format.value}"
    return await cache.retrieve_or_store(cache_key, _get_cover_thumbnail, artist, album, meme, img_quality, img_format)
