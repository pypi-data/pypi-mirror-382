from raphson_mp.client.playlist import Playlist
from raphson_mp.common.track import TRASH_PREFIX
from raphson_mp.server import server
from raphson_mp.server.track import from_relpath


async def test_delete_trash(playlist: Playlist):
    print(playlist)
    test_path = from_relpath(f"{playlist.name}/{TRASH_PREFIX}test_file")
    test_path.touch()
    assert test_path.is_file()

    # file should not be deleted
    server.trash_cleanup()
    assert test_path.is_file()

    # we cannot test if an old file will be deleted, it is not possible to change the file ctime
    # mtime cannot be used because it does not change when a file is moved (trashed)

    test_path.unlink()
