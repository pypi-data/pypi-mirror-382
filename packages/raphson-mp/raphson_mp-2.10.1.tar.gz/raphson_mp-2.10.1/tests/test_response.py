import io
from pathlib import Path
from typing import cast
from zipfile import ZipFile

from aiohttp import AsyncIterablePayload

from raphson_mp.server import response


async def test_directory_as_zip():
    resp = response.directory_as_zip(Path("docs"))

    # receive zip file
    data = io.BytesIO()
    payload = cast(AsyncIterablePayload, resp.body)
    async for part in payload._value:
        data.write(part)

    # open zip file
    zip = ZipFile(data)

    # verify that at least one file is not corrupt
    api = zip.read("tyrone_music.jpg")
    real_api = Path("docs/tyrone_music.jpg").read_bytes()
    assert api == real_api
