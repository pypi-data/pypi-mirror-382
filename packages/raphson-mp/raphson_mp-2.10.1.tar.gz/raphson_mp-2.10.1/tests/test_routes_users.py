import secrets
from sqlite3 import Connection
from typing import cast

from aiohttp.web import HTTPForbidden, HTTPSeeOther

from raphson_mp.server import auth

from . import TEST_PASSWORD, TEST_USERNAME, T_client, assert_html, user_admin


async def test_user_list_page(http_client: T_client, conn: Connection):
    async with http_client.get("/users") as response:
        assert response.status == HTTPForbidden.status_code

    with user_admin(conn):
        await assert_html(http_client, "/users")


async def test_user_edit_page(http_client: T_client, conn: Connection):
    async with http_client.get("/users/edit") as response:
        assert response.status == HTTPForbidden.status_code

    with user_admin(conn):
        await assert_html(http_client, "/users/edit?username=" + TEST_USERNAME)


async def test_user_edit(http_client: T_client, csrf_token: str, user: auth.User, conn: Connection):
    async with http_client.post("/users/edit", data={"csrf": csrf_token}) as response:
        assert response.status == HTTPForbidden.status_code

    new_username = secrets.token_urlsafe()
    new_password = secrets.token_urlsafe()

    with user_admin(conn):
        async with http_client.post(
            "/users/edit",
            data={
                "csrf": csrf_token,
                "username": TEST_USERNAME,
                "new_username": new_username,
                "new_password": new_password,
            },
            allow_redirects=False,
        ) as response:
            assert response.status == HTTPSeeOther.status_code

        # Old password should not work
        assert not await auth.verify_password(conn, user.user_id, TEST_PASSWORD)
        # Try new password
        assert await auth.verify_password(conn, user.user_id, new_password)

        # avoid properties cached in user object
        edited_user = auth.User.get(conn, user_id=user.user_id)

        # Check username
        assert edited_user.username == new_username

        # Restore username and password
        await edited_user.update_username(conn, TEST_USERNAME)
        await edited_user.update_password(conn, TEST_PASSWORD)


async def test_user_new_forbidden(http_client: T_client, csrf_token: str, conn: Connection):
    username = secrets.token_urlsafe()
    password = secrets.token_urlsafe()

    # Cannot create user as non-administrator
    async with http_client.post(
        "/users/new", data={"username": username, "password": password, "csrf": csrf_token}, allow_redirects=False
    ) as response:
        assert response.status == HTTPForbidden.status_code

    # Verify user does not exist
    assert conn.execute("SELECT id FROM user WHERE username = ?", (username,)).fetchone() is None


async def test_user_new(http_client: T_client, csrf_token: str, conn: Connection):
    username = secrets.token_urlsafe()
    password = secrets.token_urlsafe()

    with user_admin(conn):
        # Creating a user should succeed
        async with http_client.post(
            "/users/new", data={"username": username, "password": password, "csrf": csrf_token}, allow_redirects=False
        ) as response:
            assert response.status == HTTPSeeOther.status_code

        # Verify user was created correctly
        user_id = cast(int, conn.execute("SELECT id FROM user WHERE username = ?", (username,)).fetchone()[0])
        user = auth.User.get(conn, user_id=user_id)
        assert user.username == username
        assert await auth.verify_password(conn, user_id, password)

        # clean up
        conn.execute("DELETE FROM user WHERE id = ?", (user_id,))
