from tests import T_client, assert_html


async def test_player(http_client: T_client):
    await assert_html(http_client, "/player")
