## v2.10.1 2025-10-09

* New: enforce consistent usage of --offline
* Improve: hide remove from queue button on devices supporting hover with a mouse
* Improve: browser time is no longer trusted for playback history recording
* Improve: searched lyrics are now saved back to the music file
* Improve: adjustments to database indices for better performance
* Fix: errors when MediaSession API is not available
* Fix: lyrics not being searched for some tracks with no lyrics
* Fix: missing icon on PWA install page
* Fix: offline mode: track sync could be aborted if it took longer than 5 seconds

## v2.10.0 2025-10-02

Container images have been moved from GitHub to Codeberg.

| old                                 | new
| ----------------------------------- | -----------------------------------------
| `ghcr.io/DanielKoomen/WebApp`       | `codeberg.org/raphson/music-server`
| `ghcr.io/DanielKoomen/WebApp:nginx` | `codeberg.org/raphson/music-server-nginx`

Additionally, there are now tagged images available for each release, starting with v2.9.2. The :latest tag is still a rolling release.

* New: free scrolling in synced lyrics
* New: play now button in browse window
* Improve: update playlist checkboxes while music player is open when files are changed
* Improve: reduce size of track search table
* Improve: switch to trigram tokenizer, allowing search for partial words
* Improve: deduplicate tracks in albums in Subsonic API
* Improve: button to remove item from queue. In the future, clicking the album cover will be repurposed to skip to that track.
* Improve: change cookie SameSite policy from Strict to Lax
* Improve: give yt-dlp a writable, persistent cache directory
* Improve: make Containerfile compatible with architectures other than amd64
* Improve: use nicknames in charts when available
* Fix: playlist management page
* Fix: web server freeze during some offline sync operations
* Fix: settings like visualiser, theater mode not being persisted when toggled using hotkey
* Fix: error when starting remote control (playlists not loaded yet)
* Fix: performance issue in track listing in offline mode (again, now for real)
* Fix: error when autoplay is blocked by browser
* Fix: seeking in chromium-based browsers in offline mode
* Fix: missing volume icon on first page load
* Security fix: it was possible to copy a file to the root directory by using the copy file button without specifying a playlist
* Security fix: it was possible to move a file away from a playlist without write permission

## 2.9.1 2025-09-05

* Fix: performance issue in track listing in offline mode
* Fix: flashing when opening browse window

## 2.9.0 2025-09-04

The "cache" directory inside the data directory should be deleted after successfully upgrading to this version. It is no longer used.

* New: stats for "this month", "last month" instead of the last 30 days
* New: stats for current year and every past year
* New: store lyrics from online sources in metadata. You can now search in lyrics, manually edit lyrics or force a lyrics search.
* New: new "blob" system for audio and video storage, to replace cache. Missing blobs can now be generated in advance. Blobs can be immediately cleaned up when a track is deleted.
* New: security hardening for ffmpeg, fpcalc, yt-dlp using bubblewrap sandboxing
* Improve: increase size of history in player (the number of previous tracks you can skip to)
* Improve: rewrite database connection handling
* Improve: remove dependency on client time for activity, fixes issues with badly synced time on Windows
* Improve: update design of statistics page
* Improve: do not track playback history when volume is zero
* Improve: playlist management page has been overhauled
* Improve: access logs are now optional (disabled by default)
* Improve: make stats and radio available in offline mode
* Fix: incorrect ip address in access log when a proxy is in use
* Fix: metadata editing for .ogg files
* Fix: artists sometimes missing from search index
* Fix: trashed files without a music extension (.mp3, .flac, etc) were never cleaned up
* Fix: news audio was served in wav format instead of the requested audio format
* Remove: Termux scripts (deprecated for over a year)
* Remove: external cache (files in the "cache" directory)
* Technical: many code and test improvements
* Technical: update eCharts to 6.0.0
* Technical: added option to enable asyncio debug mode

## 2.8.0 2025-07-24
* Improve: hide name setting in offline mode
* Improve: support news in player sync
* Improve: replace previous toast on toggle action ("enabled" toast should replace "disabled" toast)
* Fix: client: handle errors in websocket message handler
* Technical: represent virtual tracks (like news) as normal tracks in a special ~ playlist

## 2.7.1 2025-07-13
* New: now playing on home page
* New: touch mode
* Improve: start playing before audio or cover is completely downloaded
* Improve: add close button to home page when opened from player
* Fix: player sync: tracks being skipped over
* Fix: news not being queued

## 2.7.0 2025-07-09
* New: player sync
* Improve: rewritten queue drag&drop implementation that now allows you to drop tracks in between other tracks, with a hint line
* Improve: in metadata editor, click a table row to autofill suggested metadata
* Improve: return more results in metadata editor
* Improve: rewrite browse to prepare for future merging with search
* Improve: playlist checkbox click area
* Fix: interface jumping around when skipping between tracks with and without lyrics
* Security fix: it was possible to give someone else write access to a playlist that you yourself did not have write access to

## 2.6.2 2025-06-25
* New: edit track number in metadata editor
* New: track numbers in Subsonic apps
* New: customizable client name (in play settings), shown in playing activity
* Improve: downloader: set background color of log box to red or green based on result
* Improve: verify images downloaded from bing are not corrupt
* Improve: new queue spinner
* Improve: proper icon for theater mode toast message
* Fix: news queued multiple times when paused for a long time
* Fix: missing arrow from dropdowns
* Fix: subsonic players disappearing from activity while still playing
* Technical: refactor ffmpeg, artist images, playlist code
* Technical: added tests

## 2.6.1 2025-06-18
* New: click title to browse tracks with the same title
* New: log out button
* Improve: links are no longer blue in the music player
* Improve: hide playlists without write access on downloader page
* Improve: add tooltips to buttons in browse window
* Improve: sort by title when browsing an album
* Fix: weird behaviour when going to previous track when there were no previous tracks
* Fix: cyrillic e character in lyrics (probably used to detect lyrics scraping)
* Fix: update invalid foreign key in database, resulting in various issues like being unable to create a new user account
* Technical: add many more tests
* Technical: enable testing integration in vscode

## 2.6.0 2025-06-14
* New: new background color gradient based on Raphson logo colors
* New: toast notifications
* New: track problem reporting
* New: Subsonic: artist images
* New: Subsonic: API key authentication
* New: Subsonic: scan API
* Improve: reduce seek bar CPU usage by using background color instead of subelement with changing width
* Improve: extend authentication token lifetime to 3 months
* Improve: hide playlists that are not writable from playlist dropdowns
* Improve: cover search when album metadata is not set
* Improve: hide authentication token in offline sync settings
* Improve: allow creating playlists in file manager like any other directory, instead of using a special form
* Improve: move playlist statistics to separate page
* Improve: slightly reduce CPU usage of activity page when not visible
* Improve: changed login page design
* Improve: changed table row highlight color
* Improve: remove grid lines in charts
* Improve: completely hide last.fm if not available on a server
* Improve: remove search feature in downloader, it is now possible to search directly from the download URL field
* Improve: use monospace font for downloader log
* Improve: revert to single column home layout
* Improve: sort by title when browsing by artist
* Improve: new icon for PWA install
* Fix: missing queue spinner on page load
* Fix: incorrect "seconds" unit in chart where it should be "minutes"
* Fix: ignore hotkeys when in textarea
* Fix: chairs game was broken in v2.5.0
* Fix: hardcoded English "Set up" string in WebAuthn setup
* Fix: first line missing from downloader log
* Fix: double cache write (broken locking) issue
* Fix: several bugs in radio
* Fix: Subsonic: missing album and artist images
* Fix: Subsonic: many bugs and app crashes
* Technical: build containers using podman instead of docker
* Technical: remove legacy bcrypt password hashing, users that still use bcrypt password hashes will not be able to log in
* Technical: compatibility with latest pytest-asyncio changing loop scope
* Technical: frontend preparation for remote control player
* Technical: as always, many code improvements
* Docs: update development documentation
* Docs: add browser compatibility documentation

## 2.5.0 2025-05-22
* New: share multiple tracks (playlists)
* New: add hotkeys for theater mode and visualiser
* Improve: add hint to use WebDAV to web file manager
* Improve: order playlist alphabetically, with favorite playlists first
* Improve: speed up /activity/all and /activity/files pages by reducing the number of entries from 2000 to 1000
* Improve: update seek bar less frequently to massively reduce CPU usage (over 80% of CPU was spent on updating the seek bar)
* Improve: tweak audio loudness normalizer to allow for a higher loudness range and peak, fixing rapid volume changes in songs like Nothing Else Matters by Metallica
* Fix: remove feature to avoid recently played artists, it tracks without metadata to not be played at all
* Fix: sometimes the playlist were not chosen in the correct order (multiple tracks from the same playlist in sequence)
* Fix: enabling playlist with hotkey not triggering the queue to update
* Technical: migrate to JavaScript modules
* Technical: replace eCharts with minimal version, reducing size from ~1MB to ~.5MB
* Technical: enable static analysis for JavaScript code
* Technical: enable 3 python warnings that were previously ignored

## 2.4.1 2025-03-12
* New: monochrome icon for PWA
* Improve: parallel chart loading
* Improve: hide chart legend when it contains only a single item
* Fix: dependency on cryptography module in offline module
* Fix: week 1 and 54 in "week of year" chart
* Fix: several bugs related to the file scanner, trashed files, moving files
* Fix: file manager not considering tracks without artists as music
* Fix: rare error during queue drag&drop

## 2.4.0 2025-02-24
* New: WebDAV interface
* New: WebAuthn login
* New: button to scroll to bottom in track browser
* New: show recent tracks, random tracks, or tracks with missing metadata in track browser
* New: plays by week chart
* Improve: speed up track filtering (e.g. used by track browser)
* Improve: speed up file scanner
* Improve: speed up files page
* Improve: implement resource preloading for faster page loads
* Improve: speed up Subsonic token login check
* Improve: send signal when player is closed, immediately remove from activity
* Improve: include artist and tag data in export
* Improve: highlight current row in tables in player
* Improve: wait for running tasks to complete when shutting down server
* Improve: handle moves/renames (instead of removing and then adding files)
* Improve: add labels to x and y axes for all charts
* Fix: lyrics not updating correctly when file has alternate language lyrics tags in metadata
* Fix: sorting of date values in tables
* Fix: file manager "upload file" / "create directory" buttons
* Fix: old rows not being correctly removed in activity page
* Fix: file manager using wrong URL for root directory
* Fix: missing time of day and day of week charts
* Fix: acoustid (automatic metadata discovery)
* Fix: player not loading of no previous state is saved
* Fix: sqlite WAL files keep growing
* Fix: user agent not stored for Subsonic clients
* Fix: ignore hotkeys when modifiers are pressed (e.g. don't clear queue when using Ctrl+C)
* Fix: theme color (for Safari and Chrome PWA) was set to the wrong color
* Fix: reading entire file into memory during upload
* Technical: added tests for games, account pages, static, charts, music functions, webdav, data export. Test coverage now at 71%.

## 2.3.2 2025-02-01
* New: sort table columns by clicking in header
* New: remote volume control (not yet part of UI)
* New: metrics for requests, playing/paused players
* Improve: avoid recently played artists when choosing tracks
* Improve: Subsonic: recently played and most played is now user specific
* Improve: speed up statistics loading
* Improve: speed up loading time of first track when starting player
* Fix: offline sync not updating tracks correctly
* Fix: safe handling of large body sizes in error reports
* Fix: unclosed HTTP sessions
* Technical: many code improvements and added tests

## 2.3.1 2025-01-20
* Improve: only show favorite playlists in Subsonic apps
* Fix: wait for tracks to finish syncing before exiting offline sync
* Fix: mtime and ctime mixed up
* Fix: search returning null albums
* Fix: go to album / go to artist in Subsonic apps
* Fix: outside of window click detection

## 2.3.0 2025-01-18
* New: compatibility with applications using an OpenSubsonic compatible API
* New: `c` hotkey to clear queue
* New: `l` hotkey to toggle lyrics
* New: browse tracks by year
* New: keep track of the time tracks are added (instead of only the last modification time)
* New: IP addresses and request paths are logged for unauthenticated requests
* Improve: click outside of window to close it in player
* Improve: rewritten cover thumbnail caching to be more simple and less error-prone
* Improve: add many database indices to improve performance
* Improve: use shared HTTP client connection pool to improve performance
* Improve: hide cursor in theater mode
* Improve: longer HTTP caching for images
* Improve: controls are no longer shown in activity for clients that do not support it
* Improve: show all labels in active users/playlists chart
* Improve: add rate limit to error reports to prevent abuse
* Improve: remove dashes from authentication token to allow for easy copy pasting
* Improve: add loading spinner to browse window
* Improve: search for albums using artist name instead of only album name
* Improve: add logo to login page
* Improve: only update queue HTML when changed to fix spinner animation and to improve performance
* Improve: paginate track list to speed up latency of initial tracks shown in browse window
* Improve: automatically replace ’ with ' in metadata for consistency
* Improve: do not clear manually queued tracks when clearing the queue
* Improve: offline sync web UI: more organized progress reporting and error handling
* Fix: wrong data for "long ago" in recently chosen chart
* Fix: artist instead of album artist being used for album cover search
* Fix: empty playlists missing from dropdowns (like in "copy to playlist" function)
* Fix: radio not working in insecure contexts
* Fix: untranslated strings in /activity files table
* Fix: no progress visible in activity while paused
* Fix: last.fm account linking
* Fix: wrong artist stored in track search table (apparently, this was broken since search using sqlite was first introduced)
* Docs: add last.fm
* Docs: fix Termux installation

## 2.2.0 2024-12-25
* New: API rate limiting for MusicBrainz, Reddit, last.fm
* Improve: websocket connection now works in older browser versions
* Improve: shut down more quickly when offline sync is in progress
* Improve: animate now playing progress
* Improve: enter directory immediately after creation in the file manager
* Improve: session information (last use, user agent) is now updated periodally instead of only on login
* Improve: lock cache by key to fix double work when two requests for an uncached resource are received at the same time
* Improve: move development tasks to a Makefile
* Improve: asyncio loop debug is now only enabled in development mode
* Improve: use single database connection for cache, reducing latency
* Improve: remove annoying not-allowed cursor for disabled input fields
* Improve: retry when 503 response is received from MusicBrainz
* Improve: replace loading icon by stop icon when offline sync is stopped
* Improve: reduce number of rows in /activity/all page to improve loading speed
* Fix: new data not being visible to existing database connection in some cases
* Fix: several playing activity errors for virtual tracks
* Fix: add two missing indices in track table
* Fix: album covers not being cached
* Fix: audio fingerprinting
* Fix: now playing activity progress jumping around
* Fix: some translations (LazyString) not being included in messages file
* Fix: async loop blocking during large template renders
* Fix: incremental vacuum (removing empty space from database file) not having any effect
* Fix: error when loading charts without any tracks in the database
* Remove: AAC audio format
* Technical: add and improve tests

## 2.1.1 2024-12-15
* Fix: offline mode
* Fix: standalone download script

## 2.1.0 2024-12-13
* New: websocket control channel, provides instant playing, playback history, file changes notifications
* New: remote control from activity page
* Improve: MusicBrainz album cover selection
* Improve: offline sync UI is now much more robust and fully async
* Improve: caching is disabled in development mode (start --dev)
* Improve: audio cache is no longer discarded when metadata is changed
* Technical: merged python client with this repository

## 2.0.0 2024-12-11
* New: web UI for offline sync
* New: edit lyrics in metadata editor
* New: support for time-synced lyrics in metadata (LRC format)
* Improve: performance impact of resizing music player
* Fix: clicking on playlist checkbox labels to toggle checkbox
* Fix: fresh database creation
* Fix: album cover missing in offline mode
* Fix: lyrics setting not being saved when toggled by clicking album cover image
* Remove: profiler (will be added back later)
* Technical: rewrite using aiohttp instead of Flask and requests. This opens up the ability to use websockets in the future, without needing many worker threads. Performance should also be a bit better.
* Technical: added many tests, migrate to pytest
* Technical: many tweaks to improve performance

## 1.5.0 2024-11-23

Source code is now hosted on Codeberg. To change the Git remote, use: `git remote set-url origin https://codeberg.org/raphson/music-server.git`

The offline music player should now be installed using the `raphson_mp[offline]` package instead of the bare `raphson_mp`.

* New: theming support
* New: Windows 95 theme
* Improve: layout of forms for small screens
* Improve: player layout
* Improve: many small styling updates
* Improve: home page now adapts to wider screens
* Improve: refresh authentication cookie so it does not expire during use
* Improve: remove 'today' from last chosen chart
* Fix: PWA installation button
* Fix: volume slider is now unfocused after usage to avoid hijacking hotkeys
* Fix: Spotify artist matching was case sensitive
* Technical: add command line option to enable performance profiling
* Technical: frontend errors are now reported to the backend so bugs can be more easily identified
* Technical: API clients can now provide an authentication token via the Authorization header, and skip CSRF checks

## 1.4.0 2024-11-12
* New: compare playlist with Spotify playlist
* New: support for H264 music videos
* New: fetch lyrics from LyricFind
* Improve: music video layout
* Improve: do not show "[Instrumental]" lyrics
* Improve: layout of several forms
* Improve: last chosen chart is now per playlist
* Improve: artist similarity heatmap is no longer halved and now shows relative values
* Improve: extrapolate current position in activity
* Fix: several bugs related to music videos
* Fix: adding track without metadata to queue
* Fix: too many newlines for lyrics downloaded before v1.2.0 in offline mode
* Fix: outdated lyrics showing when page was not visible while switching tracks
* Technical: database connection is now closed properly
* Technical: added tests
* Technical: many code improvements
* Meta: repository has been moved to https://github.com/Derkades/raphson-music-player

## 1.3.0 2024-11-05
* New: playlist selection in guessing game
* New: experimental music video support
* New: setting to enable or disable lyrics
* New: download data export in account settings
* Improve: highlight current lyrics line
* Improve: automatically reload if browser loads outdated player from cache
* Improve: better sizing of cover image and lyrics box, will now take up as much screen space as possible
* Improve: remove BeautifulSoup and lxml dependency
* Improve: reduce memory usage and startup time in offline mode by only importing necessary modules
* Improve: add description to settings
* Improve: login box design
* Fix: missing play button for first track
* Fix: restore missing settings button in offline mode
* Fix: copy button missing if source playlist is not writable (source doesn't need to be writable)
* Fix: broken box shadows in music player

## 1.2.1 2024-10-26
* Improve: MusicBrainz search is more likely to find the correct cover image
* Fix: album cover from cache always being low quality
* Fix: time-synced lyrics are now available in offline-mode
* Fix: language and privacy account settings were applied for all users

## 1.2.0 2024-10-22
* New: time-synced lyrics
* New: automatic metadata lookup using AcoustID and MusicBrainz
* Fix: untranslated strings

## 1.1.0 2024-10-16

* New: add track to queue from web URL
* New: hotkey to open search
* New: artist similarity heatmap in statistics
* Improve: autofocus search field
* Improve: search UI
* Improve: switch search from trigram to unicode61 tokenizer. Misspellings are no longer tolerated, but returned results are a better match.
* Improve: restore home button to offline music player
* Improve: fixed height for queue so buttons don't jump around
* Fix: missing translations in package
* Fix: broken copy button for virtual tracks (like news)

## 1.0.1 2024-10-14

* Improve: tags UI
* Fix: lyrics extraction
* Fix: null albums in search
* Fix: missing dependencies in pypi package

## 1.0.0 2024-10-13

First tagged release

## 2022-07-18

Start of development
