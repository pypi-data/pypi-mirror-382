import math
import time

from raphson_mp.server import ratelimit


async def test_ratelimit():
    TIMEOUT = 0.5

    start_time = time.time()
    limiter = ratelimit.RateLimiter(TIMEOUT)

    # first invocation should process instantly
    async with limiter:
        pass
    assert math.isclose(time.time() - start_time, 0, abs_tol=0.1)
    assert limiter.lock is not None

    # second invocation should start TIMEOUT seconds later
    async with limiter:
        assert math.isclose(time.time() - start_time, TIMEOUT, abs_tol=0.1)
        pass
    assert math.isclose(time.time() - start_time, TIMEOUT, abs_tol=0.1)

    assert limiter.release_task
    limiter.release_task.cancel()
