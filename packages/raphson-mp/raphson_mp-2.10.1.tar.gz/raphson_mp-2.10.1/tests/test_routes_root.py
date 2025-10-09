from datetime import datetime, timedelta, timezone
from sqlite3 import Connection

from multidict import CIMultiDict

from tests import T_client, assert_html


async def test_home(http_client: T_client):
    await assert_html(http_client, "/")


async def test_install(http_client: T_client):
    await assert_html(http_client, "/install")


async def test_pwa(http_client: T_client):
    async with http_client.get("/pwa") as response:
        response.raise_for_status()
        assert 'http-equiv="refresh"' in await response.text()


async def test_token(http_client: T_client, conn: Connection):
    async with http_client.get("/token") as response:
        response.raise_for_status()
        token = await response.text()

    # make sure session is created
    conn.execute("SELECT 1 FROM session WHERE token = ?", (token,)).fetchone()


async def test_healthcheck(http_client: T_client):
    async with http_client.get("/health_check") as response:
        response.raise_for_status()
        assert await response.text() == "ok"


async def test_securitytxt(http_client: T_client):
    async with http_client.get("/.well-known/security.txt") as response:
        response.raise_for_status()

        values: CIMultiDict[str] = CIMultiDict()
        for line in (await response.content.read()).splitlines():
            key, value = line.split(b": ")
            values[key.decode()] = value.decode()

        assert "Contact" in values
        assert "Preferred-Languages" in values
        expires = datetime.fromisoformat(values["Expires"])
        # must be valid for at least another 30 days
        assert expires - datetime.now(tz=timezone.utc) > timedelta(days=30)
        # must not be valid for more than one year
        assert expires - datetime.now(tz=timezone.utc) < timedelta(days=365)
