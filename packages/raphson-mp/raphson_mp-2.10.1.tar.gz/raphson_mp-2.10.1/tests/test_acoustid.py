from pathlib import Path

import pytest

from raphson_mp.server import acoustid


@pytest.mark.online
async def test_fingerprint_silence():
    fingerprint = await acoustid.get_fingerprint(Path("tests/data/test.mp3"))
    assert int(fingerprint["duration"]) == 7
    assert fingerprint["fingerprint"] == "AQAAJMkSMUkURQKAAwcA4MABAAAwAAAAAAcA56wVAA"

    # fingerprint of silence should yield no results
    results = await acoustid.lookup(fingerprint)
    assert len(results) == 0
