import json
import logging
from pathlib import Path
from typing import TypedDict, cast

from raphson_mp.common import httpclient, process
from raphson_mp.server import ratelimit, settings

if settings.offline_mode:
    # Module must not be imported to ensure no data is ever downloaded in offline mode.
    raise RuntimeError("Cannot use bing in offline mode")


log = logging.getLogger(__name__)


API_KEY = "rTTqI4IrbJ"


class LookupRecording(TypedDict):
    id: str


class LookupResult(TypedDict):
    id: str
    score: float
    recordings: list[LookupRecording]


class LookupResponse(TypedDict):
    status: str
    results: list[LookupResult]


class Fingerprint(TypedDict):
    duration: int
    fingerprint: str


async def lookup(fingerprint: Fingerprint) -> list[LookupResult]:
    """
    Returns: musicbrainz recording id
    """
    async with ratelimit.ACOUSTID:
        async with httpclient.session() as session:
            async with session.post(
                "https://api.acoustid.org/v2/lookup",
                params={
                    "format": "json",
                    "client": API_KEY,
                    "duration": int(fingerprint["duration"]),
                    "fingerprint": fingerprint["fingerprint"],
                    "meta": "recordingids",
                },
            ) as response:
                return cast(LookupResponse, await response.json())["results"]


async def get_fingerprint(path: Path) -> Fingerprint:
    stdout, _stderr = await process.run(["fpcalc", "-json", path.as_posix()], ro_mounts=[path.as_posix()])
    return cast(Fingerprint, json.loads(stdout))
