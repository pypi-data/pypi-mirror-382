import asyncio
import logging
import shutil
import tempfile
from collections.abc import AsyncIterator
from pathlib import Path
from typing import cast

from raphson_mp.common import process, util
from raphson_mp.server import auth, scanner, settings
from raphson_mp.server.playlist import Playlist

log = logging.getLogger(__name__)


if settings.offline_mode:
    # Module must not be imported to ensure no data is ever downloaded in offline mode.
    raise RuntimeError("Cannot use downloader in offline mode")


class DownloadError(Exception):
    pass


async def download(user: auth.User, dest: Playlist | Path, url_or_query: str) -> AsyncIterator[bytes]:
    cache_dir = Path(settings.data_dir, 'yt-dlp-cache').resolve()
    cache_dir.mkdir(exist_ok=True)

    temp_dir = Path(tempfile.mkdtemp())

    try:
        command = [
            "yt-dlp",
            "--cache-dir",
            cache_dir.as_posix(),
            "--format",
            "bestaudio",
            "--no-playlist",
            "--remux-video",
            "webm>ogg/mp3>mp3/mka",
            "--color",
            "never",
            "--default-search",
            "ytsearch",
            url_or_query,
        ]
        command = process.sandbox(
            command, rw_mounts=[temp_dir.as_posix(), cache_dir.as_posix()], working_dir=temp_dir.as_posix(), allow_networking=True
        )

        log.debug("running downloader command: %s", " ".join(command))
        proc = await asyncio.subprocess.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=temp_dir,  # set working dir for when sandbox is disabled
        )

        output = asyncio.StreamReader()
        process_task = asyncio.gather(
            proc.wait(),
            process.merge_streams(
                [cast(asyncio.StreamReader, proc.stdout), cast(asyncio.StreamReader, proc.stderr)], output
            ),
        )

        while line := await output.readline():
            yield line

        status_code, _none = await process_task
        if status_code != 0:
            raise DownloadError("Downloader exited with non-zero status code")

        output_files = list(temp_dir.iterdir())
        if len(output_files) == 0:
            raise DownloadError("Downloader produced no output files")
        elif len(output_files) > 1:
            raise DownloadError("Downloader produced multiple output files")
        output_file = output_files[0]
        output_size = output_file.stat().st_size
        if output_size < 10 * 1024:
            raise DownloadError("Output file is very small, something probably went wrong during the download")

        # copy file from temp dir to final output directory
        dest_dir = dest if isinstance(dest, Path) else dest.path
        dest_file = Path(dest_dir, output_file.name)
        log.info("copy file %s to %s", output_file.as_posix(), dest_file.as_posix())
        await asyncio.to_thread(shutil.copy, output_file, dest_file)

        if isinstance(dest, Playlist):
            util.create_task(scanner.scan_playlist(user, dest.name))

    finally:
        shutil.rmtree(temp_dir)
