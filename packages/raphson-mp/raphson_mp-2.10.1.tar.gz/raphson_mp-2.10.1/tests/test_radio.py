from sqlite3 import Connection

from raphson_mp.server import radio


async def test_choose_tracks(conn: Connection):
    assert radio.current_track is None
    assert radio.next_track is None

    track = await radio.get_current_track(conn)
    assert track == radio.current_track
    track2 = await radio.get_current_track(conn)
    assert track == track2
    track3 = await radio.get_next_track(conn)
    assert track3
