from __future__ import annotations

import re
from abc import ABC
from dataclasses import dataclass


class Lyrics(ABC):
    pass


@dataclass
class LyricsLine:
    start_time: float
    text: str


@dataclass
class TimeSyncedLyrics(Lyrics):
    text: list[LyricsLine]

    def to_plain(self) -> PlainLyrics:
        text = "\n".join([line.text for line in self.text])
        return PlainLyrics(text)

    def to_lrc(self) -> str:
        lrc = ""
        for line in self.text:
            minutes, seconds = divmod(line.start_time, 60)
            lrc += f"[{int(minutes):02d}:{seconds:05.2f}] {line.text}\n"
        return lrc

    @classmethod
    def from_lrc(cls, lrc: str):
        lines: list[LyricsLine] = []
        for line in lrc.splitlines():
            matches = re.findall(r"\[(\d{2}):(\d{2})\.(\d{2})\](?: (.*))?", line)
            if matches:
                minutes, seconds, centiseconds, text = matches[0]
                lines.append(LyricsLine(int(minutes) * 60 + int(seconds) + int(centiseconds) / 100, text))
        return cls(lines)


@dataclass
class PlainLyrics(Lyrics):
    text: str


INSTRUMENTAL_TEXT = "[Instrumental]"
INSTRUMENTAL_LYRICS = PlainLyrics(INSTRUMENTAL_TEXT)


def parse_lyrics(text: str | None) -> Lyrics | None:
    if text is None:
        return None
    synced = TimeSyncedLyrics.from_lrc(text)
    # TimeSyncedLyrics matcher skips lines that don't match the regex
    # if the line count is significantly lower than expected, the text is probably not in LRC format
    if len(synced.text) * 2 > text.count("\n"):
        return synced
    return PlainLyrics(text)


def lyrics_to_text(lyrics: Lyrics) -> str:
    if isinstance(lyrics, PlainLyrics):
        return lyrics.text

    if isinstance(lyrics, TimeSyncedLyrics):
        return lyrics.to_lrc()

    raise ValueError(lyrics)


def ensure_plain(lyr: Lyrics | None) -> PlainLyrics | None:
    if lyr is None:
        return None
    elif isinstance(lyr, TimeSyncedLyrics):
        return lyr.to_plain()
    elif isinstance(lyr, PlainLyrics):
        return lyr
    else:
        raise ValueError(lyr)
