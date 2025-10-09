import re


FILENAME_STRIP_KEYWORDS = [
    "(Hardstyle)",
    "(Official Music Video)",
    "[Official Music Video]",
    "(Official Video)",
    "(Official Audio)",
    "[Official Audio]",
    "[Official Video]",
    "(Official Video 4K)",
    "(Official Video HD)",
    "[FREE DOWNLOAD]",
    "(OFFICIAL MUSIC VIDEO)",
    "(live)",
    "[Radio Edit]",
    "(Clip officiel)",
    "(Audio Officiel)",
    "(Official videoclip)",
    "HQ Videoclip",
    "[Monstercat Release]",
    "[Monstercat Lyric Video]",
    "[Nerd Nation Release]",
    "[Audio]",
    "(Remastered)",
    "_ Napalm Records",
    "| Napalm Records",
    "(Lyrics)",
    "[Official Lyric Video]",
    "(Official Videoclip)",
    "(Visual)",
    "(long version)",
    " HD",
    "(Single Edit)",
    "(official video)",
    "High Quality",
    "[OUT NOW]",
    "(Dance Video)",
    "Offisiell video",
    "[FREE DL]",
    "Official Music Video",
]


ALBUM_COMPILATION_KEYWORDS = [
    "top 2000",
    "top 500",
    "top 100",
    "top 40",
    "jaarlijsten",
    "jaargang",
    "super hits",
    "the best of",
    "het beste uit",
    "hitzone",
    "greatest hits",
    "hits collection",
    "top40",
    "hitdossier",
    "100 beste",
    "top hits",
    "the very best",
    "top trax",
    "ultimate rock collection",
    "absolute music",
    "tipparade",
]


METADATA_ADVERTISEMENT_KEYWORDS = [
    "electronicfresh.com",
    "djsoundtop.com",
    "https://runderground.ru",
    "Speeeedy EDM Blog",
    "www.t.me/pmedia_music",
    "www.themusic.lt",
    "RnBXclusive.se",
]

_NORMALIZE_PATTERN = re.compile(
    r"(\(ft\. .*?\))|"
    + r"(\(feat\. .*?\))|"
    + r"(\(with .*?\))|"
    + r"(\(w/ .*?\))|"
    + r"( - ?[Rr]emastered \d{4})|"
    + r"( - \d{4} [Rr]emaster)|"
    + r"( - \d{4} [Rr]emastered version)|"
    + r"( - [Rr]emastered)|"
    + r"( - album version remastered)|"
    + r"( - rerecorded)|"
    + r"( - original version)|"
    + r"( - original mix)|"
    + r"( - radio edit)|"
    + r"( - version revisited)"
)

ALTERNATE_LYRICS_TAGS = {"lyrics-en", "lyrics-eng", "lyrics-english", "lyrics-xxx"}


def normalize_title(text: str) -> str:
    """Return lower case title with some parts removed for the purpose of matching"""
    return re.sub(_NORMALIZE_PATTERN, "", text.lower()).strip()


def album_is_compilation(album: str) -> bool:
    """Check whether album name is a compilation"""
    album = album.lower()
    for keyword in ALBUM_COMPILATION_KEYWORDS:
        if keyword in album:
            return True
    return False


def strip_keywords(inp: str) -> str:
    """
    Remove undesirable keywords from title, as a result of being downloaded from the internet.
    """
    for strip_keyword in FILENAME_STRIP_KEYWORDS:
        inp = inp.replace(strip_keyword, "")
    return inp


def join_meta_list(entries: list[str]) -> str:
    """Join list with semicolons"""
    return "; ".join(entries)


def split_meta_list(meta_list: str) -> list[str]:
    """
    Split list (stored as string in metadata) by semicolon
    """
    entries: list[str] = []
    for entry in meta_list.split(";"):
        entry = entry.strip()
        if entry != "" and entry not in entries:
            entries.append(entry)
    return entries


def has_advertisement(metadata_str: str) -> bool:
    """Check whether string contains advertisements and should be ignored"""
    for keyword in METADATA_ADVERTISEMENT_KEYWORDS:
        if keyword in metadata_str.lower():
            return True
    return False


def sort_artists(artists: list[str], album_artist: str | None) -> list[str]:
    """
    Move album artist to start of artist list
    """
    if artists and album_artist and album_artist in artists:
        artists.remove(album_artist)
        return [album_artist] + artists

    return artists
