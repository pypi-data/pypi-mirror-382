import pytest

from raphson_mp.server import reddit


@pytest.mark.online
async def test_search():
    image_url = await reddit.search("test")
    assert image_url
    assert image_url.startswith("https://"), image_url
