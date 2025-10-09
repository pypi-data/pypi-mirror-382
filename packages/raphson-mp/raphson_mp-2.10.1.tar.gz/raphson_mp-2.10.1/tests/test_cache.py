import asyncio
import secrets

from raphson_mp.server import cache


async def test_retrieve_missing():
    value = await cache.retrieve(secrets.token_urlsafe(30))
    assert value is None


async def test_store_retrieve():
    key = secrets.token_urlsafe(30)
    data = secrets.token_bytes(200)
    await cache.store(key, data, cache.HOUR)
    assert await cache.retrieve(key) == data


async def test_concurrent():
    key = secrets.token_urlsafe()
    data = secrets.token_bytes()
    func_called = False

    async def provide_data():
        # function must only be called once
        nonlocal func_called
        assert not func_called
        func_called = True

        await asyncio.sleep(0.1)
        return cache.CacheData(data, cache.DAY)

    data_list = await asyncio.gather(
        cache.retrieve_or_store(key, provide_data),
        cache.retrieve_or_store(key, provide_data),
        cache.retrieve_or_store(key, provide_data),
    )

    assert all(data == data2 for data2 in data_list)


async def test_cleanup():
    key = secrets.token_urlsafe()
    await cache.store(key, secrets.token_bytes(), 1)
    assert await cache.retrieve(key)
    await asyncio.sleep(2)
    assert await cache.retrieve(key)
    await cache.cleanup()
    assert await cache.retrieve(key) is None


async def test_memory_cache():
    key = secrets.token_urlsafe()
    data = secrets.token_bytes()
    assert cache.memory_get(key) is None
    cache.memory_store(key, data, 0.5)
    for _i in range(1000):
        cache.memory_store(secrets.token_urlsafe(), secrets.token_bytes(), 1)
    assert cache.memory_get(key) == data
    await asyncio.sleep(0.6)
    assert cache.memory_get(key) == None
