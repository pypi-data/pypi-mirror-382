from sqlite3 import Connection
from typing import cast

from tests import TEST_PASSWORD, TEST_USERNAME, T_client, assert_html


async def test_account(http_client: T_client):
    await assert_html(http_client, "/account")


def _db_password_hash(conn: Connection) -> str:
    return cast(str, conn.execute("SELECT password FROM user WHERE username=?", (TEST_USERNAME,)).fetchone()[0])


async def test_change_password(http_client: T_client, csrf_token: str, conn: Connection):
    initial_hash = _db_password_hash(conn)

    # wrong current_password
    async with http_client.post(
        "/account/change_password",
        data={
            "current_password": TEST_PASSWORD + "a",
            "new_password": "new_password",
            "repeat_new_password": "new_password",
            "csrf": csrf_token,
        },
    ) as response:
        assert response.status == 400, await response.text()
        assert _db_password_hash(conn) == initial_hash  # password should not have changed

    # correct
    async with http_client.post(
        "/account/change_password",
        data={
            "current_password": TEST_PASSWORD,
            "new_password": "new_password",
            "repeat_new_password": "new_password",
            "csrf": csrf_token,
        },
        allow_redirects=False,
    ) as response:
        assert response.status == 303, await response.text()
        assert _db_password_hash(conn) != initial_hash  # password should have changed

    # restore initial password hash
    conn.execute(
        "UPDATE user SET password = ? WHERE username = ?",
        (initial_hash, TEST_USERNAME),
    )
