"""
observe_changes() and restart() from Quart. observe_changes() was modified to
call on_change() instead of raising MustReloadError

https://github.com/pallets/quart/blob/main/src/quart/utils.py

MIT License

Copyright 2017 Pallets

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import asyncio
import logging
import os
import platform
import sys
from collections.abc import Awaitable, Callable
from pathlib import Path

_LOGGER = logging.getLogger(__name__)


async def observe_changes(on_change: Callable[[], Awaitable[None]]) -> None:
    last_updates: dict[Path, float] = {}
    for module in list(sys.modules.values()):
        filename = getattr(module, "__file__", None)
        if filename is None:
            continue
        path = Path(filename)
        try:
            last_updates[Path(filename)] = path.stat().st_mtime
        except (FileNotFoundError, NotADirectoryError):
            pass

    while True:
        await asyncio.sleep(1)

        for index, (path, last_mtime) in enumerate(last_updates.items()):
            if index % 10 == 0:
                # Yield to the event loop
                await asyncio.sleep(0)

            try:
                mtime = path.stat().st_mtime
            except FileNotFoundError:
                # File deleted
                _LOGGER.info("file deleted: %s", path.as_posix())
                await on_change()
                return
            else:
                if mtime > last_mtime:
                    _LOGGER.info("file modified: %s", path.as_posix())
                    await on_change()
                    return
                else:
                    last_updates[path] = mtime


def restart() -> None:
    # Restart  this process (only safe for dev/debug)
    executable = sys.executable
    script_path = Path(sys.argv[0]).resolve()
    args = sys.argv[1:]
    main_package = sys.modules["__main__"].__package__

    if main_package is None:
        # Executed by filename
        if platform.system() == "Windows":
            if not script_path.exists() and script_path.with_suffix(".exe").exists():
                # quart run
                executable = str(script_path.with_suffix(".exe"))
            else:
                # python run.py
                args = [str(script_path), *args]
        else:
            if script_path.is_file() and os.access(script_path, os.X_OK):
                # hypercorn run:app --reload
                executable = str(script_path)
            else:
                # python run.py
                args = [str(script_path), *args]
    else:
        # Executed as a module e.g. python -m run
        module = script_path.stem
        import_name = main_package
        if module != "__main__":
            import_name = f"{main_package}.{module}"
        args[:0] = ["-m", import_name.lstrip(".")]

    _LOGGER.info("restarting: %s", " ".join([executable] + args))
    os.execv(executable, [executable] + args)
