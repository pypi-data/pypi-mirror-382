import random
from sqlite3 import Connection

from aiohttp import web

from raphson_mp.server import auth, i18n, theme

from . import TEST_PASSWORD, TEST_USERNAME, T_client


async def test_account_page(http_client: T_client):
    async with http_client.get("/account") as response:
        response.raise_for_status()


async def test_change_settings(http_client: T_client, csrf_token: str, conn: Connection):
    data: dict[str, str | auth.PrivacyOption | None] = {
        "csrf": csrf_token,
        "nickname": random.choice(random.randbytes(4).hex()),
        "language": random.choice(list(i18n.ALL_LANGUAGE_CODES)),
        "privacy": random.choice([auth.PrivacyOption.AGGREGATE, auth.PrivacyOption.HIDDEN]).value,
        "theme": random.choice(list(theme.THEMES)),
    }
    async with http_client.post("/account/change_settings", data=data) as response:
        response.raise_for_status()

    row = conn.execute(
        "SELECT nickname, language, privacy, theme FROM user WHERE username=?", (TEST_USERNAME,)
    ).fetchone()
    assert row == (data["nickname"], data["language"], data["privacy"], data["theme"])

    # reset to default settings
    async with http_client.post(
        "/account/change_settings",
        data={
            "csrf": csrf_token,
            "nickname": "",
            "language": "",
            "privacy": "",
            "theme": theme.DEFAULT_THEME,
        },
    ) as response:
        response.raise_for_status()

    row = conn.execute(
        "SELECT nickname, language, privacy, primary_playlist, theme FROM user WHERE username=?",
        (TEST_USERNAME,),
    ).fetchone()
    assert row == (None, None, None, None, theme.DEFAULT_THEME)


async def test_change_password(http_client: T_client, csrf_token: str):
    data = {
        "csrf": csrf_token,
        "current_password": TEST_PASSWORD + "a",
        "new_password": TEST_PASSWORD,
    }
    # should fail when provided with invalid current password
    async with http_client.post("/account/change_password", data=data) as response:
        assert response.status == web.HTTPBadRequest.status_code
    # should succeed with valid password
    data["current_password"] = TEST_PASSWORD
    async with http_client.post("/account/change_password", data=data) as response:
        response.raise_for_status()
