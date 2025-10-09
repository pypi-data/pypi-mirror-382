# pyright: reportUnreachable=false
import asyncio
import random
from pathlib import Path

from aiohttp.client import ClientResponseError

from raphson_mp.client import RaphsonMusicClient
from raphson_mp.client.playlist import Playlist
from raphson_mp.client.track import Track
from raphson_mp.common.control import (
    ClientPlaying,
    ClientSubscribe,
    ServerCommand,
    ServerPlaying,
    Topic,
)
from raphson_mp.common.image import ImageFormat, ImageQuality
from raphson_mp.common.track import VIRTUAL_PLAYLIST, AudioFormat, TrackBase
from raphson_mp.server import activity, settings


def setup_module():
    settings.data_dir = Path("./data").resolve()
    settings.music_dir = Path("./music").resolve()


NEWS_TRACK = TrackBase(
    path=f"{VIRTUAL_PLAYLIST}/news",
    mtime=0,
    ctime=0,
    duration=10,
    title=None,
    album=None,
    album_artist=None,
    year=None,
    track_number=None,
    video=None,
    lyrics=None,
    artists=[],
    tags=[],
)


async def test_choose_track(client: RaphsonMusicClient, playlist: Playlist):
    try:
        await client.choose_track(playlist)
    except ClientResponseError as ex:
        if ex.status == 404:
            # 404 is fine if playlist contains no tracks
            playlist2 = await client.playlist(playlist.name)
            assert playlist2
            assert playlist2.track_count == 0
        else:
            raise ex


async def test_list_tracks(client: RaphsonMusicClient, nonempty_playlist: Playlist):
    tracks = await client.list_tracks(nonempty_playlist)
    track = random.choice(tracks)
    await client.get_track(track.path)  # verify the track exists


async def test_download_cover(client: RaphsonMusicClient, track: Track):
    await asyncio.gather(
        *[
            track.get_cover_image(client, format=format, quality=quality, meme=meme)
            for format in ImageFormat
            for quality in ImageQuality
            for meme in (False, True)
        ]
    )


async def test_now_playing(client: RaphsonMusicClient, track: Track):
    expected_virtual = False
    received_events: int = 0

    async def handler(command: ServerCommand):
        if not isinstance(command, ServerPlaying):
            return

        nonlocal received_events
        received_events += 1

        assert expected_virtual == (track.playlist == VIRTUAL_PLAYLIST)
        assert "path" in command.track
        assert command.control == False

    client.control_start(handler=handler)

    # Before subscription (should be received as soon as subscription is started)
    await client.control_send(ClientPlaying(track=track.to_dict(), paused=False, client="test"))

    # Subscribe now
    await client.control_send(ClientSubscribe(topic=Topic.PLAYING))

    # Wait for websocket receive
    async with asyncio.timeout(5):
        while received_events != 1:  # pyright: ignore[reportUnnecessaryComparison]
            await asyncio.sleep(0)

    # Send another track
    await client.control_send(ClientPlaying(track=track.to_dict(), paused=True, client="test"))

    # Wait for websocket receive
    async with asyncio.timeout(5):
        while received_events != 2:
            await asyncio.sleep(0)

    # Send news
    expected_virtual = True
    await client.control_send(ClientPlaying(track=NEWS_TRACK.to_dict(), paused=True, client="test"))

    # Wait for websocket receive
    async with asyncio.timeout(5):
        while received_events != 3:
            await asyncio.sleep(0)

    await client.control_stop()


async def test_stop(client: RaphsonMusicClient, track: Track):
    activity._NOW_PLAYING = {}
    client.control_start()
    await client.control_send(ClientPlaying(track=track.to_dict(), paused=False, client="test"))

    # wait for server to process ClientPlaying
    async with asyncio.timeout(1):
        while len(activity.now_playing()) == 0:
            await asyncio.sleep(0)

    # there should be 1 player playing
    assert len(activity.now_playing()) == 1
    await client.signal_stop()
    # now that player should be gone
    assert len(activity.now_playing()) == 0

    await client.control_stop()


# this test is at the end because it takes a while
async def test_download_audio(client: RaphsonMusicClient, track: Track):
    await asyncio.gather(*[track.get_audio(client, format) for format in AudioFormat])
