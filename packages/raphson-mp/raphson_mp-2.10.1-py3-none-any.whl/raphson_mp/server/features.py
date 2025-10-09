from enum import Enum


class Feature(Enum):
    DOWNLOADER = "downloader"
    GAMES = "games"
    WEBDAV = "webdav"
    SUBSONIC = "subsonic"
    RADIO = "radio"


FEATURES: set[Feature] = set(Feature)
