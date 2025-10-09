import asyncio
import secrets
import tracemalloc
from contextlib import contextmanager
from html.parser import HTMLParser
from pathlib import Path
from sqlite3 import Connection

from aiohttp import web
from aiohttp.test_utils import TestClient
from typing_extensions import override

from raphson_mp.client.playlist import Playlist
from raphson_mp.server import auth, db, logconfig, settings

T_client = TestClient[web.Request, web.Application]

TEST_USERNAME: str = "autotest"
TEST_PASSWORD: str = secrets.token_urlsafe()


def set_dirs():
    settings.data_dir = Path("./data").resolve()
    settings.music_dir = Path("./music").resolve()


def setup_module():
    set_dirs()
    settings.log_level = "DEBUG"
    settings.access_log = True
    logconfig.apply()

    with db.MUSIC.connect() as conn:
        conn.execute("DELETE FROM user WHERE username = ?", (TEST_USERNAME,))

        asyncio.run(auth.User.create(conn, TEST_USERNAME, TEST_PASSWORD))

    tracemalloc.start()


async def assert_html(http_client: T_client, url: str):
    async with http_client.get(url) as response:
        response.raise_for_status()
        assert response.content_type == "text/html"

        html = await response.text()

        NO_CLOSING_TAG = {"link", "img", "meta", "br", "hr", "input"}

        # perform basic checks on HTML
        class Parser(HTMLParser):
            tag_stack: list[str] = []

            def __init__(self):
                HTMLParser.__init__(self)

            @override
            def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
                if tag not in NO_CLOSING_TAG:
                    self.tag_stack.append(tag)

            @override
            def handle_endtag(self, tag: str):
                assert tag not in NO_CLOSING_TAG, f"tag {tag} should not be closed"
                expected_tag = self.tag_stack.pop()
                assert expected_tag == tag, f"expected closing tag for {expected_tag} but got {tag}"

            @override
            def handle_data(self, data: str):
                pass

        parser = Parser()
        parser.feed(html)

        assert len(parser.tag_stack) == 0, f"unclosed HTML tags: {parser.tag_stack}"


@contextmanager
def playlist_write_access(conn: Connection, playlist: Playlist):
    conn.execute(
        "INSERT OR IGNORE INTO user_playlist_write VALUES ((SELECT id FROM user WHERE username=?), ?)",
        (TEST_USERNAME, playlist.name),
    )
    yield
    conn.execute(
        "DELETE FROM user_playlist_write WHERE user = (SELECT id FROM user WHERE username=?) AND playlist = ?",
        (TEST_USERNAME, playlist.name),
    )


@contextmanager
def user_admin(conn: Connection):
    conn.execute("UPDATE user SET admin = 1 WHERE username = ?", (TEST_USERNAME,))
    yield
    conn.execute("UPDATE user SET admin = 0 WHERE username = ?", (TEST_USERNAME,))
