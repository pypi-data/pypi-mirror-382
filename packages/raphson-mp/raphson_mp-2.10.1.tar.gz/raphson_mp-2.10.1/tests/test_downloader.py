import logging
import secrets
import shutil
import tempfile
from pathlib import Path

import pytest

from raphson_mp.common import const
from raphson_mp.server import downloader
from raphson_mp.server.auth import User
from tests import T_client

_LOGGER = logging.getLogger(__name__)


async def test_invalid_format(http_client: T_client, user: User):
    dest = Path(tempfile.mkdtemp())
    try:
        download_url = str(http_client.make_url("/static/img/raphson.png"))
        lines: list[bytes] = []
        with pytest.raises(downloader.DownloadError):
            async for line in downloader.download(user, dest, download_url):
                lines.append(line)
        assert b"raphson: Requested format is not available" in lines[-1]
    finally:
        shutil.rmtree(dest)


async def test_download(http_client: T_client, user: User):
    test_mp3 = Path("tests/data/test.mp3")
    src_filename = secrets.token_urlsafe(8) + ".mp3"
    src_path = Path(const.STATIC_PATH, src_filename)
    dest = Path(tempfile.mkdtemp())
    try:
        shutil.copy(test_mp3, src_path)
        download_url = str(http_client.make_url("/static/" + src_filename))
        async for _line in downloader.download(user, dest, download_url):
            _LOGGER.info(_line)
        assert src_path.read_bytes() == test_mp3.read_bytes()
    finally:
        shutil.rmtree(dest)
        src_path.unlink()
