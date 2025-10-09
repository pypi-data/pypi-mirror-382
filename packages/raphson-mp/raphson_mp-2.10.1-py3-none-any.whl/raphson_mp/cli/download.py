import json
import os
import time
from pathlib import Path
from typing import TypedDict, cast

from raphson_mp.client import RaphsonMusicClient
from raphson_mp.client.track import Track
from raphson_mp.common.track import AudioFormat

SETTINGS_PATH = Path("download-settings.json")


class Settings(TypedDict):
    server: str
    token: str


class Downloader:
    client: RaphsonMusicClient

    def __init__(self):
        self.client = RaphsonMusicClient()

    async def setup(self, settings: Settings):
        await self.client.setup(base_url=settings["server"], token=settings["token"], user_agent="Downloader")

    async def download_track(self, track: Track, local_path: Path):
        local_path.write_bytes(await track.get_audio(self.client, AudioFormat.MP3_WITH_METADATA))

    async def download_playlist(self, playlist_name: str):
        tracks = await self.client.list_tracks(playlist_name)
        playlist_path = Path(playlist_name).resolve()
        all_local_paths: set[str] = set()

        for track in tracks:
            local_path = Path(track.path[: track.path.rindex(".")] + ".mp3").resolve()
            all_local_paths.add(local_path.as_posix())
            # don't allow directory traversal by server
            if not local_path.is_relative_to(playlist_path):
                raise RuntimeError(f"Path: {local_path.as_posix()} not relative to {playlist_path}")

            if local_path.exists():
                mtime = int(local_path.stat().st_mtime)
                if mtime != track.mtime:
                    print("Update: " + track.path)
                else:
                    print("OK: " + track.path)
                    continue
            else:
                print("Download: " + track.path)
                local_path.parent.mkdir(exist_ok=True)

            await self.download_track(track, local_path)
            os.utime(local_path, (time.time(), track.mtime))

        # Prune deleted tracks
        for track_path in playlist_path.glob("**/*"):
            track_path = track_path.resolve()
            if track_path.as_posix() not in all_local_paths:
                print("Delete: " + track_path.as_posix())
                track_path.unlink()


async def start(playlist: str):
    if SETTINGS_PATH.is_file():
        settings = cast(Settings, json.loads(SETTINGS_PATH.read_text()))
    else:
        print("Not configured, please log in")
        server = input("Server URL: ").rstrip("/")
        token = input("Token: ")
        settings: Settings = {"server": server, "token": token}
        SETTINGS_PATH.write_text(json.dumps(settings))

    downloader = Downloader()
    try:
        await downloader.setup(settings)
        await downloader.download_playlist(playlist)
    finally:
        await downloader.client.close()
