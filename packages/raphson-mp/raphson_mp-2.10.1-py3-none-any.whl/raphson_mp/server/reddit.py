import logging
import random

from raphson_mp.common import httpclient
from raphson_mp.server import ratelimit, settings

if settings.offline_mode:
    # Module must not be imported to ensure no data is ever downloaded in offline mode.
    raise RuntimeError("Cannot use reddit in offline mode")

log = logging.getLogger(__name__)

MEME_SUBREDDITS = [
    "me_irl",
    "meme",
    "memes",
    "ik_ihe",
    "wholesomememes",
    "wholesomegreentext",
    "greentext",
    "antimeme",
    "misleadingthumbnails",
    "wtfstockphotos",
    "AdviceAnimals",
]

SUBREDDIT_ATTEMPTS = 2


async def _search(subreddit: str | None, query: str) -> str | None:
    log.info("searching subreddit %s for: %s", subreddit if subreddit else "ALL", query)

    params = {
        "q": query,
        "raw_json": "1",
        "type": "link",
    }

    if subreddit is None:
        subreddit = "all"  # doesn't matter
    else:
        params["restrict_sr"] = "1"

    async with ratelimit.REDDIT:
        async with httpclient.session("https://www.reddit.com") as session:
            async with session.get(f"/r/{subreddit}/search.json", params=params) as response:
                json = await response.json()

    assert json["kind"] == "Listing"

    posts = json["data"]["children"]
    for post in posts:
        if post["kind"] == "t3":
            if "post_hint" in post["data"] and post["data"]["post_hint"] == "image":
                return post["data"]["preview"]["images"][0]["source"]["url"]

    return None


async def search(query: str) -> str | None:
    """
    Search several subreddits for an image
    Args:
        query: Search query
    Returns: Image URL string, or None if no image was found
    """
    subreddits: list[str] = random.choices(MEME_SUBREDDITS, k=SUBREDDIT_ATTEMPTS)
    # subreddits.append(None) # If nothing was found, search all of reddit
    for subreddit in subreddits:
        url = await _search(subreddit, query)
        if url is not None:
            return url
    return None


async def get_image(query: str) -> bytes | None:
    """
    Search several subreddits for an image, and download it
    Args:
        query: Search query string
    Returns: Downloaded image bytes, or None if no image was found or an error occurred
    """
    image_url = await search(query)
    if image_url is None:
        return None

    async with httpclient.session() as session:
        async with session.get(image_url) as response:
            if response.status != 200:
                log.warning("Received status code %s while downloading image from Reddit", response.status)
                return None
            return await response.content.read()
