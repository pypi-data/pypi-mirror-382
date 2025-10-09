import asyncio
import logging
from typing import NotRequired, TypedDict, Unpack, cast

from raphson_mp.server import settings

_LOGGER = logging.getLogger(__name__)


class ProcessReturnCodeError(Exception):
    code: int

    def __init__(self, code: int, stdout: bytes, stderr: bytes):
        super().__init__(f"Process ended with code {code}", stdout[:4096], stderr[:4096])
        self.code = code


async def _write(process: asyncio.subprocess.Process, data: bytes | None):
    if data is not None:
        stdin = cast(asyncio.StreamWriter, process.stdin)
        try:
            stdin.write(data)
            await stdin.drain()
        except ConnectionResetError:
            pass
        stdin.close()


class SandboxOptions(TypedDict):
    rw_mounts: NotRequired[list[str]]
    ro_mounts: NotRequired[list[str]]
    working_dir: NotRequired[str]
    allow_networking: NotRequired[bool]


def sandbox(
    command: list[str],
    rw_mounts: list[str] | None = None,
    ro_mounts: list[str] | None = None,
    working_dir: str | None = None,
    allow_networking: bool = False,
):
    """
    Use bwrap to run the given command in a sandbox. If bwrap is disabled, the original command is returned.
    """
    if not settings.bwrap:
        return command

    if rw_mounts is None:
        rw_mounts = []
    if ro_mounts is None:
        ro_mounts = []

    ro_mounts.append("/usr")
    ro_mounts.append("/etc")
    # TODO make library loading work without mounting entire /etc
    # ffmpeg: error while loading shared libraries: libjack.so.0: cannot open shared object file: No such file or directory
    # ro_mounts.append("/etc/ld.so.conf.d")
    # ro_mounts.append("/etc/ld.so.conf")

    if allow_networking:
        # on systems with systemd-resolved, /etc/resolv.conf is symlinked to a file inside /run/systemd/resolve
        ro_mounts.append("/run/systemd/resolve")

    symlinks = [("usr/lib64", "/lib64"), ("usr/bin", "/bin")]

    sandboxed_command = ["bwrap"]

    sandboxed_command.append("--new-session")
    sandboxed_command.append("--unshare-all")
    if allow_networking:
        sandboxed_command.append("--share-net")

    for path in rw_mounts:
        sandboxed_command.extend(("--bind", path, path))

    for path in ro_mounts:
        sandboxed_command.extend(("--ro-bind", path, path))

    for path_from, path_to in symlinks:
        sandboxed_command.extend(("--symlink", path_from, path_to))

    if working_dir is not None:
        sandboxed_command.extend(("--chdir", working_dir))

    sandboxed_command.append("--die-with-parent")
    sandboxed_command.append("--clearenv")

    sandboxed_command.append("--")
    sandboxed_command.extend(command)

    return sandboxed_command


async def run(command: list[str], input: bytes | None = None, **kwargs: Unpack[SandboxOptions]) -> tuple[bytes, bytes]:
    command = sandbox(command, **kwargs)
    _LOGGER.debug("running subprocess: %s", " ".join(command))
    process = await asyncio.subprocess.create_subprocess_exec(
        *command,
        stdin=asyncio.subprocess.PIPE if input is not None else None,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=kwargs.get("working_dir"),  # set working directory for when sandbox is disabled
    )

    stdout, stderr, code, _none = await asyncio.gather(
        cast(asyncio.StreamReader, process.stdout).read(),
        cast(asyncio.StreamReader, process.stderr).read(),
        process.wait(),
        _write(process, input),
    )

    if code != 0:
        raise ProcessReturnCodeError(code, stdout, stderr)

    return stdout, stderr


async def merge_streams(streams: list[asyncio.StreamReader], output_stream: asyncio.StreamReader):
    """Merge streams (e.g. stdout/stderr) line by line. Also replaces carriage return by line feed."""

    async def copy(stream: asyncio.StreamReader):
        # TODO when updated to Python 3.13, use readuntil with a tuple
        previous = b""
        while part := await stream.read(65536):
            # contrary to StreamReader.readline(), bytes.splitlines() does consider \r as a line break
            lines = (previous + part).splitlines(keepends=True)
            for line in lines:
                if line[-1] == ord("\n"):
                    output_stream.feed_data(line)
                elif line[-1] == ord("\r"):
                    output_stream.feed_data(line[:-1] + b"\n")
                else:
                    previous = line
        output_stream.feed_data(previous)

    try:
        await asyncio.gather(*(copy(stream) for stream in streams))
    finally:
        # all input streams have been read completely or an error occurred, feed EOF
        output_stream.feed_eof()
