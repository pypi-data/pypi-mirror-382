import pytest

from raphson_mp.server import musicbrainz


@pytest.mark.online
async def test_correct_release():
    # Should find album, not single
    rg_id = await musicbrainz._search_release_group("Red Hot Chili Peppers", "Californication")
    assert rg_id == "ca5dfcc3-83fb-3eee-9061-c27296b77b2c"

    # Should find "Nocturnal" by "The Midnight", not "Nocturnal Transmissions" by "The Midnight Ensemble"
    rg_id = await musicbrainz._search_release_group("The Midnight", "Nocturnal")
    assert rg_id == "71ab4ae6-0211-41a4-9adb-abe85efa77ed"


@pytest.mark.online
async def test_cover():
    cover = await musicbrainz.get_cover("SebastiAn", "Dancing By Night")
    assert cover
    assert len(cover) > 400000


@pytest.mark.online
async def test_metadata():
    metas = musicbrainz.get_recording_metadata("a8fe7228-18fc-40d9-80c6-cbfb71d5d03e")
    async for meta in metas:
        assert meta.album in {"The Remixes", "Dancing By Night"}
        assert meta.year == 2023
        assert "London Grammar" in meta.artists
        assert "SebastiAn" in meta.artists
