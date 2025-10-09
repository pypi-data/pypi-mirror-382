import random
import secrets
from typing import cast

from raphson_mp.common.typing import GetCsrfResponseDict
from tests import TEST_PASSWORD, TEST_USERNAME, T_client, assert_html


async def test_login_html(http_client: T_client):
    await assert_html(http_client, "/auth/login")


async def test_login_fail(http_client: T_client):
    async with http_client.post(
        "/auth/login", json={"username": TEST_USERNAME, "password": secrets.token_urlsafe(random.randint(1, 100))}
    ) as response:
        assert response.status == 403, await response.text()


async def test_login_json(http_client: T_client):
    async with http_client.post("/auth/login", json={"username": TEST_USERNAME, "password": TEST_PASSWORD}) as response:
        assert response.status == 200
        token = cast(str, (await response.json())["token"])
        assert len(token) > 10


async def test_get_csrf(http_client: T_client):
    async with http_client.get("/auth/get_csrf") as response:
        json = cast(GetCsrfResponseDict, await response.json())
        assert "token" in json
