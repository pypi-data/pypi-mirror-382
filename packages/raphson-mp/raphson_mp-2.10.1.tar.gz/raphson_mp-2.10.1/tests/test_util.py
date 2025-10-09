import asyncio
import io
import math
import random
from io import BytesIO
import time
from unittest import mock

import pytest
from aiohttp import StreamReader, web
from aiohttp.test_utils import make_mocked_request

from raphson_mp.common import util


def test_is_mobile():
    # collection of most common user agents from https://useragents.me

    mobiles = [
        "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.3",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.",
        "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/26.0 Chrome/122.0.0.0 Mobile Safari/537.3",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0.1 Mobile/15E148 Safari/604.",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.90 Mobile/15E148 Safari/604.",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.90 Mobile/15E148 Safari/604.",
        "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.3",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) GSA/340.3.689937600 Mobile/15E148 Safari/604.",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.90 Mobile/15E148 Safari/604.",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) GSA/340.3.689937600 Mobile/15E148 Safari/604.",
        "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36 OPR/85.0.0.",
        "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.3",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.90 Mobile/15E148 Safari/604.",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_7_10 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_7_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.",
        "Mozilla/5.0 (Android 13; Mobile; rv:132.0) Gecko/132.0 Firefox/132.",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Mobile/15E148 YisouSpider/5.0 Safari/604.",
    ]

    desktops = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.1",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.3",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.3",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.3",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.1958",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.3",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.91 Safari/537.3",
    ]

    tablets = [
        "Mozilla/5.0 (iPad; CPU OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/132.0 Mobile/15E148 Safari/605.1.15",
        "Mozilla/5.0 (iPad; CPU OS 17_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1",
    ]

    for mobile in mobiles:
        assert util.is_mobile(make_mocked_request(method="GET", path="/", headers={"User-Agent": mobile})), mobile

    for desktop in [*desktops, *tablets]:
        assert not util.is_mobile(make_mocked_request(method="GET", path="/", headers={"User-Agent": desktop})), desktop


def test_substr_keyword():
    assert util.substr_keyword("HE[LLO{text[[", "{", "[") == "text"


async def test_queueio():
    print(util)
    queue_io = util.AsyncQueueIO()
    assert not queue_io.seekable()
    assert not queue_io.readable()

    def write():
        for _i in range(32):
            data = bytes(1024 * 1024) + b"a"
            queue_io.write(data)
        queue_io.close()

    buf = BytesIO()

    async def read():
        async for data in queue_io.iterator():
            buf.write(data)

    await asyncio.gather(asyncio.to_thread(write), read())

    assert buf.tell() == 32 * (1024 * 1024 + 1)
    buf.seek(-1, io.SEEK_CUR)
    assert buf.read(1) == b"a"
    buf.seek(0)
    assert buf.read(1) == b"\00"
    buf.seek(1024 * 1024)
    assert buf.read(1) == b"a"


def test_str_match_approx():
    assert util.str_match_approx("hello", "hello")
    assert util.str_match_approx("HeLLo", "hello")
    assert util.str_match_approx("hello hello", "hello_hello")
    assert not util.str_match_approx("goodbye", "hello")


def test_urlencode():
    assert util.urlencode(" /") == "%20%2F"


async def test_cancel_tasks():
    task = asyncio.create_task(asyncio.sleep(300))
    await util.cancel_tasks({task})
    assert task.cancelled()


async def test_get_content_bounded():
    # request without Content-Length should return bad request
    request = make_mocked_request("GET", "/")
    with pytest.raises(web.HTTPBadRequest):
        await util.get_content_bounded(request)

    max_length = 1000

    # Too high Content-Length header
    request = make_mocked_request("GET", "/", headers={"Content-Length": str(max_length + 1)})
    with pytest.raises(web.HTTPRequestEntityTooLarge):
        await util.get_content_bounded(request, max_length=max_length)

    # Lie in Content-Length header and actually send more data
    reader = StreamReader(mock.Mock(), 5000)
    reader.feed_data(random.randbytes(2000))
    request = make_mocked_request("GET", "/", headers={"Content-Length": "500"}, payload=reader)
    data2 = await util.get_content_bounded(request, max_length=max_length)
    assert len(data2) == 500


async def test_create_await_task():
    task = util.create_task(asyncio.sleep(0.1))
    assert not task.done()
    assert len(util.TASKS) == 1
    await util.await_tasks()
    assert task.done()
    assert len(util.TASKS) == 0


async def test_await_tasks_timeout():
    util.create_task(asyncio.sleep(3600))
    time1 = time.time()
    async with asyncio.timeout(2):
        await util.await_tasks(0.5)
        time2 = time.time()
        assert math.isclose(time1, time2, abs_tol=0.1)
