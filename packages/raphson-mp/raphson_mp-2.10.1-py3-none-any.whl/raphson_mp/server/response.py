import asyncio
import time
from pathlib import Path
from typing import Any
from zipfile import ZipFile

from aiohttp import web

from raphson_mp.common import util
from raphson_mp.server import settings
from raphson_mp.server.vars import JINJA_ENV, USER


async def template(template_name: str, *args: Any, **kwargs: Any) -> web.Response:
    template = JINJA_ENV.get().get_template(template_name)
    html_str = template.generate_async(
        *args,
        user=USER.get(),
        offline_mode=settings.offline_mode,
        load_timestamp=int(time.time()),
        **kwargs,
    )

    async def encoder():
        i = 0
        async for part in html_str:
            # periodically yield to event loop, for large template renders
            i += 1
            if i % 100 == 0:
                await asyncio.sleep(0)

            yield part.encode()

    return web.Response(body=encoder(), status=200, content_type="text/html")


def _directory_as_zip(queue_io: util.AsyncQueueIO, path: Path):
    try:
        with ZipFile(queue_io, "w") as zf:
            for subpath in path.glob("**/*"):
                zf.write(subpath, arcname=subpath.relative_to(path))
    finally:
        queue_io.close()


def directory_as_zip(path: Path) -> web.Response:
    if not path.is_dir():
        raise NotADirectoryError(path)
    queue_io = util.AsyncQueueIO()
    util.create_task(asyncio.to_thread(_directory_as_zip, queue_io, path))
    return web.Response(
        body=queue_io.iterator(),
        content_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{path.name}.zip"'},
    )


def file_attachment(path: Path) -> web.StreamResponse:
    return web.FileResponse(path, headers={"Content-Disposition": f'attachment; filename="{path.name}"'})
