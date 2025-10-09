import asyncio

from raphson_mp.common import const
from raphson_mp.common.image import ImageFormat, ImageQuality
from raphson_mp.server import bing, cache, ffmpeg, spotify


async def _artist_image_data(artist: str):
    # Try Spotify
    if spotify_client := spotify.client():
        if image := await spotify_client.get_artist_image(artist):
            return cache.CacheData(image, cache.YEAR)

    # Try Bing
    if image := await bing.image_search(artist + " artist"):
        return cache.CacheData(image, cache.HALFYEAR)

    image = await asyncio.to_thread(const.RAPHSON_PNG_PATH.read_bytes)
    return cache.CacheData(image, cache.WEEK)


def artist_image(artist: str):
    return cache.retrieve_or_store(f"artistimg{artist}", _artist_image_data, artist)


async def _artist_image_thumbnail_data(artist: str, img_format: ImageFormat, img_quality: ImageQuality):
    image = await artist_image(artist)
    thumbnail = await ffmpeg.image_thumbnail(image, img_format, img_quality, True)
    return cache.CacheData(thumbnail, cache.MONTH)


def artist_image_thumbnail(artist: str, img_format: ImageFormat, img_quality: ImageQuality):
    return cache.retrieve_or_store(
        f"artistimgthumb{artist}", _artist_image_thumbnail_data, artist, img_format, img_quality
    )
