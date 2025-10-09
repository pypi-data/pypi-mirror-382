import asyncio
import json
import logging
from html.parser import HTMLParser
from typing import cast

import aiohttp
from typing_extensions import override

from raphson_mp.common import httpclient
from raphson_mp.server import ffmpeg, settings

log = logging.getLogger(__name__)


if settings.offline_mode:
    # Module must not be imported to ensure no data is ever downloaded in offline mode.
    raise RuntimeError("Cannot use bing in offline mode")


async def _download(session: aiohttp.ClientSession, image_url: str) -> bytes | None:
    """
    Download image by URL
    Args:
        image_url
    Returns: Image bytes, or None if the image failed to download
    """
    try:
        async with session.get(image_url) as response:
            img_bytes = await response.content.read()
    except (aiohttp.ClientError, TimeoutError):
        log.info("could not download %s, connection error", image_url)
        return None

    log.info("downloaded image: %s", image_url)

    return img_bytes


async def _download_all(session: aiohttp.ClientSession, image_urls: list[str]) -> list[bytes]:
    """
    Download multiple images, returning the image of the largest size first (probably the
    highest quality image)
    """
    maybe_downloads = await asyncio.gather(*[_download(session, image_url) for image_url in image_urls])

    # Remove failed downloads
    downloads = [d for d in maybe_downloads if d is not None]

    def _sort_key(download: bytes) -> int:
        return len(download)

    return sorted(downloads, key=_sort_key)


async def image_search(bing_query: str) -> bytes | None:
    """
    Perform image search using Bing
    Parameters:
        bing_query: Search query
    Returns: Image data bytes
    """
    log.info("searching bing: %s", bing_query)
    try:
        async with httpclient.session(scraping=True) as session:
            async with session.get(
                "https://www.bing.com/images/search",
                params={
                    "q": bing_query,
                    "form": "HDRSC2",
                    "first": "1",
                    "scenario": "ImageBasicHover",
                },
                cookies={"SRCHHPGUSR": "ADLT=OFF"},  # disable safe search :-)
            ) as response:
                text = await response.text()

            class Parser(HTMLParser):
                image_urls: list[str] = []

                @override
                def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
                    if tag != "a":
                        return

                    attrs_dict = dict(attrs)

                    if "class" not in attrs_dict:
                        return

                    if attrs_dict["class"] != "iusc":
                        return

                    if "m" not in attrs_dict:
                        return

                    m_attr: str = cast(str, attrs_dict["m"])
                    image_url = cast(str, json.loads(m_attr)["murl"])
                    self.image_urls.append(image_url)

            parser = Parser()
            parser.feed(text)

            images = await _download_all(session, parser.image_urls[:5])
            for image in images:
                if await ffmpeg.check_image(image):
                    return image
                else:
                    log.info("skipping a corrupt image")
            return None
    except Exception:
        log.info("error during bing search (this is probably a bug)", exc_info=True)
        return None
