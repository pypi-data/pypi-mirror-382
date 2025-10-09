from raphson_mp.common import metadata


def test_normalize():
    assert metadata.normalize_title("Pizza (ft. Japser) - remastered 2008") == "pizza"


def test_compilation():
    assert not metadata.album_is_compilation("Momentary Lapse Of Reason")
    assert metadata.album_is_compilation("Top 40 jaren 80")
    assert metadata.album_is_compilation("Super hitzone")
    assert metadata.album_is_compilation("The Best of Michael Jackson")


def test_metalist():
    assert metadata.split_meta_list("A;B ; C") == ["A", "B", "C"]
    assert metadata.join_meta_list(["A", "B", "C"]) == "A; B; C"


def test_ad():
    assert metadata.has_advertisement("djsoundtop.com")
    assert not metadata.has_advertisement("hello")


def test_sort():
    assert metadata.sort_artists(["A", "B"], "B") == ["B", "A"]
