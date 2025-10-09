import asyncio
import difflib
import io
import logging
import time
import urllib.parse
from collections.abc import AsyncIterator, Coroutine
from contextlib import contextmanager, suppress
from io import BytesIO, IOBase
from typing import Any, TypeVar

from _asyncio import Task
from aiohttp import web
from typing_extensions import override

_LOGGER = logging.getLogger(__name__)
MOBILE_FLAGS = ["Android", "iPhone"]


def is_mobile(request: web.Request) -> bool:
    """
    Checks whether User-Agent looks like a mobile device (Android or iOS)
    """
    if "User-Agent" in request.headers:
        user_agent = request.headers["User-Agent"]
        for flag in MOBILE_FLAGS:
            if flag in user_agent:
                return True
    return False


# TODO use io.Writer as base class when project requires Python 3.14
class AsyncQueueIO(IOBase):
    queue: asyncio.Queue[bytes | None]
    loop: asyncio.AbstractEventLoop
    buf: BytesIO

    def __init__(self) -> None:
        self.queue = asyncio.Queue(maxsize=32)
        self.loop = asyncio.get_running_loop()
        self.buf = BytesIO()

    @override
    def close(self):
        super().close()

        async def finish():
            pos = self.buf.tell()
            self.buf.seek(0)
            remaining_data = self.buf.read(pos)
            await self.queue.put(remaining_data)
            await self.queue.put(None)

        asyncio.run_coroutine_threadsafe(finish(), self.loop)

    @override
    def readable(self):
        return False

    @override
    def seekable(self):
        return False

    @override
    def write(self, data: bytes):
        written = self.buf.write(data)

        # thread-safe writing to the queue is an expensive operation
        # buffer writes locally up to 1MB
        pos = self.buf.tell()
        if pos > 1024 * 1024:
            self.buf.seek(0)
            bulk_data = self.buf.read(pos)
            self.buf.seek(0)
            asyncio.run_coroutine_threadsafe(self.queue.put(bulk_data), self.loop)

        return written

    async def iterator(self) -> AsyncIterator[bytes]:
        while True:
            data = await self.queue.get()
            if data is None:
                return

            yield data


def str_match_approx(a: str, b: str) -> bool:
    if a == b:
        return True

    a = a.lower()
    b = b.lower()

    if a == b:
        return True

    diff = difflib.SequenceMatcher(None, a, b)
    # real_quick_ratio() provides an upper bound on quick_ratio(), which provides an upper bound on ratio()
    # ratio() is expensive so we must avoid it when possible
    return diff.real_quick_ratio() > 0.8 and diff.quick_ratio() > 0.8 and diff.ratio() > 0.8


def substr_keyword(text: str, start: str, end: str):
    start_i = text.index(start) + len(start)
    end_i = start_i + text[start_i:].index(end)
    return text[start_i:end_i]


@contextmanager
def log_duration(task: str):
    start = time.monotonic_ns()
    yield None
    end = time.monotonic_ns()
    _LOGGER.debug("%s took %.3f", task, (end - start) / 1e9)


def urlencode(text: str) -> str:
    return urllib.parse.quote(text, safe="")


T_TaskReturn = TypeVar("T_TaskReturn")


async def cancel_tasks(tasks: set[asyncio.Task[T_TaskReturn]]):
    for task in tasks:
        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass


async def get_content_bounded(request: web.Request, max_length: int = 1024) -> bytes:
    length = request.content_length
    if length is None:
        raise web.HTTPBadRequest(reason="Content-Length must be specified")

    if length > max_length:
        raise web.HTTPRequestEntityTooLarge(max_length, length)

    return await request.content.read(length)


TASKS: set[asyncio.Task[Any]] = set()
T_CreateTask_Return = TypeVar("T_CreateTask_Return")


def create_task(coro: Coroutine[Any, Any, T_CreateTask_Return]) -> Task[T_CreateTask_Return]:
    task = asyncio.create_task(coro)
    TASKS.add(task)

    def remove_task(task: Task[T_CreateTask_Return]):
        with suppress(KeyError):
            TASKS.remove(task)

    task.add_done_callback(remove_task)
    return task


async def await_tasks(timeout: float | None = None):
    if len(TASKS) == 0:
        return

    _done, pending_tasks = await asyncio.wait(TASKS, timeout=timeout)

    for task in pending_tasks:
        stringio = io.StringIO()
        task.print_stack(file=stringio)
        _LOGGER.warning("task still running: %s", stringio.getvalue())
