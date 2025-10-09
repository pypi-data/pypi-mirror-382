from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from raphson_mp.common.lyrics import PlainLyrics, TimeSyncedLyrics
from raphson_mp.server.lyrics import (
    AZLyricsFetcher,
    GeniusFetcher,
    LrcLibFetcher,
    MuzikumFetcher,
)


@pytest.mark.online
async def test_lrclib_online():
    # full length cd version
    lyrics = await LrcLibFetcher().find("Strong", "London Grammar", "If You Wait", 276)
    assert isinstance(lyrics, TimeSyncedLyrics), lyrics
    assert lyrics.text[0].text == "Excuse me for a while", lyrics.text[0]
    assert lyrics.text[0].start_time == 43.56, lyrics.text[0]

    # music video version
    lyrics = await LrcLibFetcher().find("Strong", "London Grammar", "If You Wait", 242)
    assert isinstance(lyrics, TimeSyncedLyrics), lyrics
    assert lyrics.text[0].text == "Excuse me for a while", lyrics.text[0]
    assert lyrics.text[0].start_time == 14.6, lyrics.text[0]


async def test_azlyrics():
    azlyrics = AZLyricsFetcher()
    azlyrics.get_html = AsyncMock()
    azlyrics.get_html.return_value = Path("tests/data/azlyrics.html").read_text()
    lyrics = await azlyrics.find("Starburster", "Fontaines D.C.", None, None)
    assert lyrics and lyrics.text == Path("tests/data/azlyrics_out.txt").read_text().rstrip("\n")


@pytest.mark.online
async def test_azlyrics_online():
    lyrics = await AZLyricsFetcher().find("Starburster", "Fontaines D.C.", None, None)
    assert lyrics and lyrics.text == Path("tests/data/azlyrics_out.txt").read_text().rstrip("\n")


@pytest.mark.online
async def test_genius_online():
    lyrics = await GeniusFetcher().find("Give Me One Reason", "Tracy Chapman", None, None)
    assert isinstance(lyrics, PlainLyrics)
    assert "You know that I called you, I called too many times" in lyrics.text, lyrics.text


# @pytest.mark.online
# async def test_lyricfind():
#     lyrics = await LyricFindFetcher().find("Blank Space", "Taylor Swift", None, None)
#     assert isinstance(lyrics, PlainLyrics)
#     assert "Nice to meet you, where you been?" in lyrics.text, lyrics.text


async def test_muzikum_slug():
    assert MuzikumFetcher.to_slug("De Dijk") == "de-dijk"
    assert MuzikumFetcher.to_slug("J'Adore") == "jadore"


async def test_muzikum():
    input_html = Path("tests/data/muzikum.html").read_text()
    output_text = Path("tests/data/muzikum_out.txt").read_text().rstrip("\n")

    muzikum = MuzikumFetcher()
    muzikum.get_html = AsyncMock()
    muzikum.get_html.return_value = input_html

    lyrics = await muzikum.find("", "", None, None)
    assert lyrics and lyrics.text == output_text

    # test with None return value
    muzikum.get_html.return_value = None
    lyrics = await muzikum.find("", "", None, None)
    assert lyrics is None


@pytest.mark.online
async def test_muzikum_online():
    output_text = Path("tests/data/muzikum_out.txt").read_text().rstrip("\n")
    muzikum = MuzikumFetcher()
    lyrics = await muzikum.find("Nu of Nou", "De Dijk", None, None)
    assert lyrics and lyrics.text == output_text
