import io
import json
from zipfile import ZipFile

from . import T_client


async def test_export(http_client: T_client):
    async with http_client.get("/export/data") as response:
        assert response.status == 200
        assert response.content_type == "application/zip"
        temp = io.BytesIO()
        temp.write(await response.read())
        temp.seek(0)
        with ZipFile(temp, "r") as zf:
            userjson = zf.read("user.json")
            json.loads(userjson)  # verify it is valid json
