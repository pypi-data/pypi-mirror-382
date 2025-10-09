import html
import json
import logging
import re
import time
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from html.parser import HTMLParser
from typing import Any, cast

import aiohttp
from typing_extensions import override

from raphson_mp.common import httpclient, util
from raphson_mp.common.lyrics import (
    INSTRUMENTAL_LYRICS,
    INSTRUMENTAL_TEXT,
    Lyrics,
    PlainLyrics,
    TimeSyncedLyrics,
    lyrics_to_text,
)
from raphson_mp.server import db, scanner, settings, unicodefixer
from raphson_mp.server.track import FileTrack, get_track

if settings.offline_mode:
    # Module must not be imported to ensure no data is ever downloaded in offline mode.
    raise RuntimeError("Cannot use lyrics module in offline mode")

log = logging.getLogger(__name__)


class LyricsFetcher(ABC):
    name: str
    supports_synced: bool

    @abstractmethod
    async def find(self, title: str, artist: str, album: str | None, duration: int | None) -> Lyrics | None:
        pass


class LrcLibFetcher(LyricsFetcher):
    name: str = "lrclib.net"
    supports_synced: bool = True

    def _json_to_lyrics(self, json: Any) -> Lyrics | None:
        if json["syncedLyrics"]:
            return TimeSyncedLyrics.from_lrc(json["syncedLyrics"])

        if json["plainLyrics"]:
            return PlainLyrics(json["plainLyrics"])

    @override
    async def find(self, title: str, artist: str, album: str | None, duration: int | None) -> Lyrics | None:
        params: dict[str, str] = {"track_name": title, "artist_name": artist}
        if album is not None:
            params["album_name"] = album
        if duration is not None:
            params["duration"] = str(duration)
        async with httpclient.session("https://lrclib.net") as session:
            async with session.get("/api/get", params=params, raise_for_status=False) as response:
                if response.status != 404:
                    response.raise_for_status()
                    return self._json_to_lyrics(await response.json())

            log.info("lrclib: no results for direct get, trying search")
            async with session.get(
                "/api/search", params={"artist_name": artist, "track_name": title}, raise_for_status=True
            ) as response:
                json = await response.json()
                if len(json) == 0:
                    return None
                json = json[0]

                # Sanity check on title and artist
                if not util.str_match_approx(artist, json["artistName"]):
                    return None
                if not util.str_match_approx(title, json["trackName"]):
                    return None

                return self._json_to_lyrics(json)


class MusixMatchFetcher(LyricsFetcher):
    """
    Based on (but heavily modified):
    https://gitlab.com/ronie/script.cu.lrclyrics/-/blob/master/lib/culrcscrapers/musixmatchlrc/lyricsScraper.py

    MIT License

    Copyright (c) 2022 Momo

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
    """

    name: str = "MusixMatch"
    supports_synced: bool = True

    _cached_token: str | None = None
    _cached_token_expiration_time: int = 0

    async def get_token(self, session: aiohttp.ClientSession) -> str | None:
        if self._cached_token and int(time.time()) < self._cached_token_expiration_time:
            return self._cached_token

        async with session.get(
            "token.get", params={"user_language": "en", "app_id": "web-desktop-app-v1.0", "t": int(time.time())}
        ) as response:
            result = await response.json(content_type="text/plain")  # MusixMatch uses wrong Content-Type for JSON

        if "message" in result:
            message = result["message"]
            if (
                "header" in message
                and "status_code" in message
                and message["status_code"] == 401
                and "hint" in message
                and message["hint"] == "captcha"
            ):
                log.warning("cannot obtain MusixMatch token, captcha is required")
                return None

            if "body" in message and "user_token" in message["body"]:
                token = message["body"]["user_token"]
                self._cached_token = token
                self._cached_token_expiration_time = int(time.time()) + 600
                return token

        raise ValueError("could not obtain token", result)

    async def get_lyrics_from_list(self, session: aiohttp.ClientSession, track_id: str) -> str | None:
        token = await self.get_token(session)
        if token is None:
            return None

        async with session.get(
            "track.subtitle.get",
            params={
                "track_id": track_id,
                "subtitle_format": "lrc",
                "app_id": "web-desktop-app-v1.0",
                "usertoken": token,
                "t": str(int(time.time())),
            },
        ) as response:
            try:
                result = await response.json(content_type="text/plain")  # MusixMatch uses wrong Content-Type for JSON
            except json.JSONDecodeError:
                log.warning("MusixMatch: failed to decode json: %s", response.text)
                return None

        if "message" in result:
            if (
                "header" in result["message"]
                and "status_code" in result["message"]["header"]
                and result["message"]["header"]["status_code"] == 404
            ):
                return None

            if (
                "body" in result["message"]
                and "subtitle" in result["message"]["body"]
                and "subtitle_body" in result["message"]["body"]["subtitle"]
            ):
                lyrics = result["message"]["body"]["subtitle"]["subtitle_body"]
                return lyrics

        log.warning("unexpected response: %s", result)
        return None

    @override
    async def find(self, title: str, artist: str, album: str | None, duration: int | None):
        async with httpclient.session(
            "https://apic-desktop.musixmatch.com/ws/1.1/",
            headers={
                "authority": "apic-desktop.musixmatch.com",
                "cookie": "AWSELBCORS=0; AWSELB=0",
            },
            scraping=True,
        ) as session:
            token = await self.get_token(session)
            if token is None:
                return None

            async with session.get(
                "track.search",
                params={
                    "q": title + " " + artist,
                    "page_size": 5,
                    "page": 1,
                    "app_id": "web-desktop-app-v1.0",
                    "usertoken": token,
                    "t": int(time.time()),
                },
            ) as response:
                try:
                    result = await response.json(
                        content_type="text/plain"
                    )  # MusixMatch uses wrong Content-Type for JSON
                except json.JSONDecodeError:
                    log.warning("MusixMatch: failed to decode json: %s", response.text)
                    return None

            if (
                "message" in result
                and "body" in result["message"]
                and "track_list" in result["message"]["body"]
                and result["message"]["body"]["track_list"]
            ):
                for item in result["message"]["body"]["track_list"]:
                    found_artist = item["track"]["artist_name"]
                    found_title = item["track"]["track_name"]
                    found_track_id = item["track"]["track_id"]
                    log.info("musixmatch: search result: %s: %s - %s", found_track_id, found_artist, found_title)
                    if not util.str_match_approx(title, found_title) and util.str_match_approx(artist, found_artist):
                        continue

                    lyrics = await self.get_lyrics_from_list(session, found_track_id)
                    if lyrics is None or lyrics == "":
                        # when this happens, the website shows "Unfortunately we're not authorized to show these lyrics..."
                        log.info("musixmatch: lyrics are empty")
                        continue

                    return TimeSyncedLyrics.from_lrc(lyrics)

            return None


class AZLyricsFetcher(LyricsFetcher):
    """
    Adapted from: https://gitlab.com/ronie/script.cu.lrclyrics/-/blob/master/lib/culrcscrapers/azlyrics/lyricsScraper.py
    Licensed under GPL v2
    """

    name: str = "AZLyrics"
    supports_synced: bool = False

    async def get_html(self, artist: str, title: str) -> str | None:
        artist = re.sub("[^a-zA-Z0-9]+", "", artist).lower().lstrip("the ")
        title = re.sub("[^a-zA-Z0-9]+", "", title).lower()

        async with httpclient.session("https://www.azlyrics.com", scraping=True) as session:
            async with session.get(f"/lyrics/{artist}/{title}.html", raise_for_status=False) as response:
                if response.status == 404:
                    return None
                response.raise_for_status()
                return await response.text()

    @override
    async def find(self, title: str, artist: str, album: str | None, duration: int | None) -> PlainLyrics | None:
        text = await self.get_html(artist, title)
        if text is None:
            return None

        lyricscode = text.split("t. -->")[1].split("</div")[0]
        lyricstext = html.unescape(lyricscode).replace("<br />", "\n")
        lyrics = re.sub("<[^<]+?>", "", lyricstext).lstrip("\r\n").rstrip()
        return PlainLyrics(lyrics)


class GeniusFetcher(LyricsFetcher):
    name: str = "Genius"
    supports_synced: bool = False

    @override
    async def find(self, title: str, artist: str, album: str | None, duration: int | None) -> PlainLyrics | None:
        async with httpclient.session(scraping=True) as session:
            url = await self._search(session, title, artist)
            if url is None:
                return None

            lyrics = await self._extract_lyrics(session, url)
            if lyrics is None:
                return None

            return PlainLyrics(lyrics)

    async def _search(self, session: aiohttp.ClientSession, title: str, artist: str) -> str | None:
        """
        Returns: URL of genius lyrics page, or None if no page was found.
        """
        async with session.get(
            "https://genius.com/api/search/multi", params={"per_page": "1", "q": title + " " + artist}
        ) as response:
            search_json = await response.json()
            for section in search_json["response"]["sections"]:
                if section["type"] == "top_hit":
                    for hit in section["hits"]:
                        if hit["index"] == "song":
                            if util.str_match_approx(title, hit["result"]["title"]):
                                return hit["result"]["url"]
                    break

            return None

    def _html_to_lyrics(self, html: str) -> str:
        # Extract text from HTML tags
        # Source HTML contains <p>, <b>, <i>, <a> etc. with lyrics inside.
        class Parser(HTMLParser):
            text: str = ""

            def __init__(self):
                HTMLParser.__init__(self)

            @override
            def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
                if tag == "br":
                    self.text += "\n"

            @override
            def handle_data(self, data: str):
                self.text += data.strip()

        parser = Parser()
        parser.feed(html)
        return parser.text

    async def _extract_lyrics(self, session: aiohttp.ClientSession, genius_url: str) -> str | None:
        """
        Extract lyrics from the supplied Genius lyrics page
        Parameters:
            genius_url: Lyrics page URL
        Returns: A list where each element is one lyrics line.
        """
        # Firstly, a request is made to download the standard Genius lyrics page. Inside this HTML is
        # a bit of inline javascript.
        async with session.get(genius_url) as response:
            text = await response.text()

        # Find the important bit of javascript using known parts of the code
        text = util.substr_keyword(text, "window.__PRELOADED_STATE__ = JSON.parse('", "');")

        # Inside the javascript bit that has now been extracted, is a string. This string contains
        # JSON data. Because it is in a string, some characters are escaped. These need to be
        # un-escaped first.
        text = (
            text.replace('\\"', '"').replace("\\'", "'").replace("\\\\", "\\").replace("\\$", "$").replace("\\`", "`")
        )

        # Now, the JSON object is ready to be parsed.
        try:
            info_json = json.loads(text)
        except json.decoder.JSONDecodeError as ex:
            log.info("error retrieving lyrics: json decode error at %s", ex.pos)
            log.info('neighbouring text: "%s"', text[ex.pos - 20 : ex.pos + 20])
            raise ex

        # For some reason, the JSON object happens to contain lyrics HTML. This HTML is parsed.
        lyrics_html = info_json["songPage"]["lyricsData"]["body"]["html"]
        lyrics_text = self._html_to_lyrics(lyrics_html)
        if lyrics_text.lower() in {
            "instrumental",
            "[instrumental]",
            "[instrument]",
            "(instrumental)",
            "♫ instrumental ♫",
            "*instrumental*",
        }:
            return INSTRUMENTAL_TEXT
        return lyrics_text


class LyricFindFetcher(LyricsFetcher):
    # https://lyrics.lyricfind.com/openapi.spec.json
    name: str = "LyricFind"
    supports_synced: bool = False

    @override
    async def find(self, title: str, artist: str, album: str | None, duration: int | None) -> PlainLyrics | None:
        async with httpclient.session("https://lyrics.lyricfind.com", scraping=True) as session:
            async for slug in self._search(session, title, artist, duration):
                try:
                    return await self._get(session, slug)
                except Exception:
                    log.warning("error in LyricFind lyrics search", exc_info=True)
                    continue
            return None

    async def _search(
        self, session: aiohttp.ClientSession, title: str, artist: str, duration: int | None
    ) -> AsyncIterator[str]:
        async with session.get(
            "/api/v1/search",
            params={
                "reqtype": "default",
                "territory": "NL",
                "searchtype": "track",
                "track": title,
                "artist": artist,
                "limit": 10,
                "output": "json",
                "useragent": httpclient.WEBSCRAPING_USER_AGENT,
            },
        ) as response:

            for track in (await response.json())["tracks"]:
                if not util.str_match_approx(title, track["title"]):
                    continue

                if not util.str_match_approx(artist, track["artist"]["name"]) and artist not in [
                    artist["name"] for artist in track["artists"]
                ]:
                    continue

                log.info("found result: %s - %s", track["artist"]["name"], track["title"])

                if duration and "duration" in track:
                    duration_str = track["duration"]
                    duration_int = int(duration_str.split(":")[0]) * 60 + int(duration_str.split(":")[1])

                    if abs(duration - duration_int) > 5:
                        log.info("duration not close enough")
                        continue

                yield track["slug"]

    async def _get(self, session: aiohttp.ClientSession, slug: str) -> PlainLyrics | None:
        # 'https://lyrics.lyricfind.com/api/v1/lyric' exists but seems to always return unauthorized
        # use a web scraper instead :-)

        url = "/lyrics/" + slug
        log.info("LyricFind: downloading from: %s", url)
        async with session.get(url) as response:
            response_html = await response.text()
            response_json = util.substr_keyword(
                response_html, '<script id="__NEXT_DATA__" type="application/json">', "</script>"
            )
            track_json = json.loads(response_json)["props"]["pageProps"]["songData"]["track"]
            if "lyrics" in track_json:
                return PlainLyrics(track_json["lyrics"])
            else:
                # Instrumental
                return None


class MuzikumFetcher(LyricsFetcher):
    name: str = "Muzikum"
    supports_synced: bool = False

    @staticmethod
    def to_slug(name: str):
        return re.sub(r"[^a-zA-Z0-9\ ]+", "", name).lower().replace(" ", "-")

    async def get_html(self, title: str, artist: str) -> str | None:
        artist = self.to_slug(artist)
        title = self.to_slug(title)

        async with httpclient.session(scraping=True) as session:
            async with session.get(
                f"https://muzikum.eu/en/{util.urlencode(artist)}/{util.urlencode(title)}-lyrics", allow_redirects=False
            ) as response:
                if response.status == 200:
                    return await response.text()
                elif response.status in {301, 404}:
                    return None
                else:
                    raise ValueError(response.status)

    def parse_html(self, html: str):
        class Parser(HTMLParser):
            text: str = ""
            in_tag: bool = False

            def __init__(self):
                HTMLParser.__init__(self)

            @override
            def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
                if tag == "pre":
                    for attr in attrs:
                        if attr[1] == "whitespace-pre-line text-normal md:text-lg":
                            self.in_tag = True

            @override
            def handle_endtag(self, tag: str) -> None:
                self.in_tag = False

            @override
            def handle_data(self, data: str):
                if self.in_tag:
                    self.text += data

        parser = Parser()
        parser.feed(html)
        return parser.text if parser.text != "" else None

    @override
    async def find(self, title: str, artist: str, album: str | None, duration: int | None) -> PlainLyrics | None:
        html = await self.get_html(title, artist)
        if html is None:
            return None
        text = self.parse_html(html)
        if text is None:
            return None
        return PlainLyrics(text)


FETCHERS: list[LyricsFetcher] = [
    #                       ratelimit   time-synced   duration
    LrcLibFetcher(),  #     none        yes           yes
    MusixMatchFetcher(),  # bad         yes           no
    # LyricFindFetcher(),  #bad         no            yes
    GeniusFetcher(),  #     good        no            no
    AZLyricsFetcher(),  #   unknown     no            no
    # MuzikumFetcher(),  #    unknown     no            no
]


async def find_lyrics(title: str, artist: str, album: str | None, duration: int | None) -> Lyrics | None:
    log.info("searching lyrics for: %s - %s", artist, title)

    plain_match: Lyrics | None = None
    error_count = 0

    for fetcher in FETCHERS:
        if plain_match is not None and not fetcher.supports_synced:
            # if we already have plain lyrics, we do not need to try any fetchers that only support plain lyrics
            continue

        try:
            lyrics = await fetcher.find(title, artist, album, duration)
        except Exception as ex:
            log.warning("%s: encountered an error: %s", fetcher.name, ex)
            log.debug("", exc_info=True)
            error_count += 1
            continue

        if lyrics is None:
            log.info("%s: no lyrics found, continuing search", fetcher.name)
            continue

        if isinstance(lyrics, TimeSyncedLyrics):
            log.info("%s: found time-synced lyrics", fetcher.name)
            return lyrics

        if plain_match:
            log.info("%s, no time-synced lyrics found, continuing search", fetcher.name)
            continue

        if isinstance(lyrics, PlainLyrics):
            log.info("%s: found plain lyrics, continuing search", fetcher.name)
            plain_match = lyrics
            continue

        raise ValueError(lyrics)

    # No time-synced lyrics found

    if plain_match is not None:
        log.info("returning plain lyrics")
        return plain_match

    if error_count >= len(FETCHERS) / 2:
        log.info("more than half of fetchers returned an error, is the internet connection working?")
        return None

    log.info("no lyrics found, assuming instrumental")
    return INSTRUMENTAL_LYRICS


async def find_task():
    """
    Runs periodically. Finds a track in the database that has the required metadata but does not have lyrics stored
    yet. Finds lyrics for this track and stores it in the database.
    """
    # Find a track without lyrics
    with db.MUSIC.connect() as conn:
        row = cast(
            tuple[str] | None,
            conn.execute(
                """
                SELECT path
                FROM track
                WHERE lyrics IS NULL AND
                    title IS NOT NULL AND
                    (
                        album_artist IS NOT NULL OR
                        EXISTS(SELECT artist FROM track_artist WHERE track=path)
                    )
                LIMIT 1
                """
            ).fetchone(),
        )
        if row is None:
            return

        track = await get_track(conn, row[0])

    assert isinstance(track, FileTrack)

    # Search lyrics for this track
    title = track.title
    artist = track.primary_artist
    assert title and artist

    log.info("fetching lyrics for: %s", track.path)

    lyrics = await find_lyrics(title, artist, track.album, track.duration)
    if lyrics is None:
        return

    lyrics_text = lyrics_to_text(lyrics)
    lyrics_text = unicodefixer.fix(lyrics_text)

    track.lyrics = lyrics_text
    await track.save()
    await scanner.scan_track(None, track.filepath)
