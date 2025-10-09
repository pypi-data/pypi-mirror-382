import math
from pathlib import Path
from sqlite3 import Connection
from tempfile import NamedTemporaryFile

from raphson_mp.client.track import Track
from raphson_mp.common.track import AudioFormat
from raphson_mp.server.blob import BLOB_TYPES, AudioBlob, _blob_path, _new_blob_id
from raphson_mp.server.track import FileTrack


async def test_blob_id():
    blob_id = _new_blob_id()
    assert not blob_id.endswith("=")
    assert len(blob_id) > 10


async def test_blob_path():
    blob_id = _new_blob_id()
    path = _blob_path(blob_id)
    assert path.name == blob_id[2:]
    assert path.parent.name == blob_id[:2]
    assert path.parent.name + path.name == blob_id


async def test_missing(conn: Connection):
    # delete a random blob so there is something to generate
    conn.execute('DELETE FROM blob WHERE rowid = (SELECT rowid FROM blob ORDER BY RANDOM() LIMIT 1);')

    for blob_type in BLOB_TYPES:
        blob = blob_type.missing()
        if blob is not None:
            row = conn.execute(
                "SELECT * FROM blob WHERE track = ? AND blobtype = ?", (blob.track.path, blob.blobtype)
            ).fetchone()
            assert row is None  # blob must actually be missing

            await blob.get()
            row = conn.execute(
                "SELECT * FROM blob WHERE track = ? AND blobtype = ?", (blob.track.path, blob.blobtype)
            ).fetchone()
            assert row is not None  # blob must now exist


async def test_audioblob_produce(conn: Connection, track: Track):
    filetrack = FileTrack(conn, track.path)
    blob = AudioBlob(filetrack, AudioFormat.WEBM_OPUS_HIGH)
    with NamedTemporaryFile() as tempfile:
        output_path = Path(tempfile.name)
        output_path.touch()
        await blob.produce(output_path)

        expected_size = (128_000 // 8) * filetrack.duration
        actual_size = output_path.stat().st_size

        # check if size is within 10% of expected size
        # this ensures the file is written properly and the bitrate is passed correctly to ffmpeg
        assert math.isclose(expected_size, actual_size, rel_tol=0.1)
