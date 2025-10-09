import asyncio

import pytest

from raphson_mp.common import process


async def test_run():
    await asyncio.gather(*[process.run(["true"], input=b"a") for _i in range(100)])

    with pytest.raises(process.ProcessReturnCodeError):
        await process.run(["false"])


async def test_output():
    stdout, stderr = await process.run(["cat"], input=b"hello")
    assert stdout == b"hello"
    assert stderr == b""

    with pytest.raises(process.ProcessReturnCodeError):
        await process.run(["python3", "--WRONGFLAG"])

    stdout, stderr = await process.run(["ffmpeg", "--help"])
    assert stdout.startswith(b"Universal media converter")
    assert stderr.startswith(b"ffmpeg version")
