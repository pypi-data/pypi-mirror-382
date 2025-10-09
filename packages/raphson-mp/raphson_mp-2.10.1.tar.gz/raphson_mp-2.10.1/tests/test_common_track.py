from raphson_mp.common.track import AudioFormat, TrackBase, relpath_playlist

TRACK = TrackBase(
    path="Playlist/Subdir/Track [Official Music Video] [A7scmQjsd].wav",
    mtime=0,
    ctime=0,
    duration=300,
    title="Title",
    album="Album",
    album_artist="Album Artist",
    year=2000,
    track_number=1,
    video=None,
    lyrics=None,
    artists=["Artist1", "Artist2"],
    tags=["Tag1", "Tag2"],
)


def test_trackbase():
    assert TRACK.playlist == "Playlist"
    assert TRACK.filename == "Track [Official Music Video] [A7scmQjsd].wav"
    assert TRACK._filename_title() == "Track"
    assert TRACK.display_title() == "Artist1, Artist2 - Title (Album, 2000)"
    assert TRACK.display_title(show_year=False) == "Artist1, Artist2 - Title (Album)"
    assert TRACK.display_title(show_album=False) == "Artist1, Artist2 - Title (2000)"
    assert TRACK.display_title(show_album=False, show_year=False) == "Artist1, Artist2 - Title"
    assert TRACK.download_name() == "Artist1, Artist2 - Title (Album, 2000)"
    # just check it does not throw an error
    TRACK.mtime_dt
    TRACK.ctime_dt
    TRACK.to_dict()


def test_trackbase_primaryartist():
    TRACK.album_artist = "Artist1"
    assert TRACK.primary_artist == "Artist1"
    TRACK.album_artist = "Artist2"
    assert TRACK.primary_artist == "Artist2"
    TRACK.album_artist = None
    assert TRACK.primary_artist in {"Artist1", "Artist2"}


def test_audioformat():
    assert AudioFormat.MP3_WITH_METADATA.content_type == "audio/mp3"
    assert AudioFormat.WEBM_OPUS_HIGH.content_type == "audio/webm"
    assert AudioFormat.WEBM_OPUS_LOW.content_type == "audio/webm"


def test_relpath_playlist():
    assert relpath_playlist("RS") == "RS"
    assert relpath_playlist("RS/A/B") == "RS"
