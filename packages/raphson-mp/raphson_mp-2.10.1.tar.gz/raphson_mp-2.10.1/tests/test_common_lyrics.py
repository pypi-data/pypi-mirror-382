from raphson_mp.common.lyrics import (
    LyricsLine,
    PlainLyrics,
    TimeSyncedLyrics,
    parse_lyrics,
)


def test_lrc_convert():
    lrc = """
[01:24.06] And the tide's gonna turn
[01:25.56] And it's all gonna roll your way
[01:28.26] Workin' 9 to 5, what a way to make a livin'
[01:33.31]
"""
    lyrics = TimeSyncedLyrics.from_lrc(lrc)
    lrc2 = lyrics.to_lrc()
    assert lrc.strip() == lrc2.strip()
    assert lyrics.text[0] == LyricsLine(84.06, "And the tide's gonna turn")


def test_synced_to_plain():
    lyrics = TimeSyncedLyrics([LyricsLine(0, "hello"), LyricsLine(1, "world")])
    plain = lyrics.to_plain().text
    assert plain.splitlines()[0] == "hello"


def test_parse():
    assert parse_lyrics(None) is None

    lrc = """
[00:09.59] Tumble outta bed and I stumble to the kitchen
[00:12.08] Pour myself a cup of ambition
[00:14.16] And yawn and stretch and try to come to life
[00:19.09] Jump in the shower and the blood starts pumpin'
[00:21.75] Out on the street, the traffic starts jumpin'
"""
    assert isinstance(parse_lyrics(lrc), TimeSyncedLyrics)

    plain = """
Tumble outta bed and I stumble to the kitchen
Pour myself a cup of ambition
And yawn and stretch and try to come to life
Jump in the shower and the blood starts pumpin'
Out on the street, the traffic starts jumpin'
"""
    assert isinstance(parse_lyrics(plain), PlainLyrics)
