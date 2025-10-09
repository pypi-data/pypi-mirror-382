# Raphson Music Player

Web-based social music player for communities (hacker spaces, maker spaces).

What makes this different from other music players? It is designed around listening with groups. Instead of playing a single playlist, this music player allows enabling many playlists from different people. Tracks are shuffled from multiple playlists into a single queue. No more arguing about which music to play, everyone's music get played.

An additional benefit of this is music discovery, even when you're listening solo you might like to mix up your own music with someone else's.

![Screenshot of music player](https://downloads.rkslot.nl/music-player-screenshots/player6-small.webp)

## Features

- Shuffle
    - Shuffle algorithm ensures the least recently played songs are picked first.
    - Of course, you can also manually browse or search the music collection and queue specific songs.
- Gets out of your way
    - The number of clicks required to perform any action should be minimal. Buttons should be large and not hidden behind submenus.
    - Hotkeys are available to speed up common actions
- Responsive and mobile compatible
    - Touch-friendly interface.
    - Low quality audio/image option is available to save data
    - Implements the (Open)Subsonic protocol, allowing you to use native apps
- Metadata management
    - Large, high quality album covers are automatically fetched from MusicBrainz
    - Time synced lyrics are automatically fetched from various sources
    - Metadata editor to easily correct metadata while listening
    - Audio is loudness-normalized ensuring consistent volume for all genres, without losing dynamic range.
- File management
    - Built-in web file browser to download, upload, rename and delete files
    - WebDAV protocol support allows you to connect with an external file manager application
    - Built-in music downloader using `yt-dlp`
- Statistics
    - See what others are playing now or in the past
    - Statistics page with graphs based on historical data
    - Last.fm scrobbling (each user can connect their own last.fm account)
- News
    - Optionally, play hourly news just like real radio.
- Fun
    - Enable 'Album cover meme mode' to replace album covers by (sometimes) funny memes related to the song title.
    - Play games with your music collections, like a music guessing game.
- Simple, minimal, fast and secure
    - Written in pure HTML, CSS and JavaScript with only one third party library (eCharts). The frontend should be fast, even on an old laptop or cheap single board computer.
    - Queued songs are cached, temporary network connection issues are no problem.
    - Python dependencies are kept to a minimum (aiohttp, jinja2, babel, cryptography).
    - Very strict Content-Security-Policy allows no communication from clients to the internet.
    - The server is simple to run with one command. No other services, like a database, are needed.

## Screenshots

See [docs/screenshots.md](docs/screenshots.md) (will load ~20MB of images).

## Usage

See [docs/installation.md](docs/installation.md).

## Related projects

- [Headless client](https://codeberg.org/raphson/music-headless): to run on a headless machine with an audio output. Can be controlled remotely.
- [Headless client HA](https://codeberg.org/raphson/music-headless-ha): Home Assistant integration to control a headless client.

## Development and translation

See [docs/development.md](docs/development.md).
