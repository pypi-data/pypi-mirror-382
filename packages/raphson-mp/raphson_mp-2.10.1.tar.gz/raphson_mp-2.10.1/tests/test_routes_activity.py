from tests import T_client, assert_html


async def test_activity(http_client: T_client):
    await assert_html(http_client, "/activity")


async def test_files(http_client: T_client):
    await assert_html(http_client, "/activity/files")


async def test_all(http_client: T_client):
    await assert_html(http_client, "/activity/all")
