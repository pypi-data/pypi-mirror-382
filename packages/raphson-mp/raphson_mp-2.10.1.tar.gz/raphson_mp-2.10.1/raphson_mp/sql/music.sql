BEGIN;

CREATE TABLE playlist (
    name TEXT NOT NULL UNIQUE PRIMARY KEY
) STRICT;

CREATE TABLE track (
    path TEXT NOT NULL UNIQUE PRIMARY KEY,
    playlist TEXT NOT NULL REFERENCES playlist(name) ON DELETE CASCADE,
    duration INTEGER NOT NULL,
    title TEXT NULL COLLATE NOCASE,
    album TEXT NULL COLLATE NOCASE,
    album_artist TEXT NULL COLLATE NOCASE,
    track_number INTEGER NULL,
    year INTEGER NULL,
    mtime INTEGER NOT NULL,
    ctime INTEGER NOT NULL,
    last_chosen INTEGER NOT NULL DEFAULT 0,
    lyrics TEXT NULL,
    video TEXT NULL
) STRICT;

CREATE INDEX idx_track_filter ON track(path, playlist, title, album, album_artist, year, mtime, ctime);
CREATE INDEX idx_track_playlist_duration ON track(playlist, duration); -- SELECT COUNT(*), COALESCE(SUM(duration), 0) FROM track WHERE playlist=?

CREATE TRIGGER track_insert AFTER INSERT ON track BEGIN
    INSERT INTO track_fts (rowid, path, title, album, album_artist, lyrics) VALUES (new.rowid, new.path, new.title, new.album, new.album_artist, new.lyrics);
END;

CREATE TRIGGER track_delete AFTER DELETE ON track BEGIN
    DELETE FROM track_fts WHERE rowid = old.rowid;
END;

CREATE TRIGGER track_update AFTER UPDATE ON track BEGIN
    UPDATE track_fts
        SET path = d.path, title = d.title, album = d.album, album_artist = d.album_artist, lyrics = d.lyrics, artists = d.artists
        FROM (SELECT path, title, album, album_artist, lyrics, GROUP_CONCAT(artist, ' ') AS artists FROM track JOIN track_artist ON path = track WHERE track.rowid = new.rowid GROUP BY path) AS d
        WHERE track_fts.rowid = new.rowid;
END;

CREATE TABLE track_artist (
    track TEXT NOT NULL REFERENCES track(path) ON DELETE CASCADE ON UPDATE CASCADE,
    artist TEXT NOT NULL COLLATE NOCASE,
    UNIQUE (track, artist)
) STRICT;

CREATE INDEX idx_track_artist_track ON track_artist(track);
CREATE INDEX idx_track_artist_artist ON track_artist(artist);

CREATE TRIGGER track_artist_insert AFTER INSERT ON track_artist BEGIN
    UPDATE track_fts
        SET path = d.path, title = d.title, album = d.album, album_artist = d.album_artist, lyrics = d.lyrics, artists = d.artists
        FROM (SELECT track.rowid AS rowid, path, title, album, album_artist, lyrics, GROUP_CONCAT(artist, ' ') AS artists FROM track JOIN track_artist ON path = track WHERE path = new.track GROUP BY path) AS d
        WHERE track_fts.rowid = d.rowid;
END;

CREATE TRIGGER track_artist_delete AFTER DELETE ON track_artist BEGIN
    UPDATE track_fts
        SET path = d.path, title = d.title, album = d.album, album_artist = d.album_artist, lyrics = d.lyrics, artists = d.artists
        FROM (SELECT track.rowid AS rowid, path, title, album, album_artist, lyrics, GROUP_CONCAT(artist, ' ') AS artists FROM track JOIN track_artist ON path = track WHERE path = old.track GROUP BY path) AS d
        WHERE track_fts.rowid = d.rowid;
END;

CREATE TABLE track_tag (
    track TEXT NOT NULL REFERENCES track(path) ON DELETE CASCADE ON UPDATE CASCADE,
    tag TEXT NOT NULL COLLATE NOCASE,
    UNIQUE (track, tag)
) STRICT;

CREATE INDEX idx_track_tag_track ON track_tag(track);
CREATE INDEX idx_track_tag_tag ON track_tag(tag);

CREATE TABLE track_problem (
    track TEXT NOT NULL UNIQUE REFERENCES track(path) ON DELETE CASCADE ON UPDATE CASCADE
) STRICT;

CREATE TABLE track_loudness (
    track TEXT NOT NULL UNIQUE REFERENCES track(PATH) ON DELETE CASCADE ON UPDATE CASCADE,
    input_i REAL NOT NULL,
    input_tp REAL NOT NULL,
    input_lra REAL NOT NULL,
    input_thresh REAL NOT NULL,
    target_offset REAL NOT NULL
) STRICT;

CREATE TABLE user (
    id INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    nickname TEXT NULL,
    password TEXT NULL,
    admin INTEGER NOT NULL DEFAULT 0,
    primary_playlist TEXT NULL REFERENCES playlist(name) ON DELETE SET NULL,
    language TEXT NULL,
    privacy TEXT NULL,
    theme TEXT NOT NULL DEFAULT 'default'
) STRICT;

CREATE TABLE user_playlist_favorite (
    user INTEGER NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    playlist TEXT NOT NULL REFERENCES playlist(name) ON DELETE CASCADE,
    UNIQUE (user, playlist)
) STRICT;

CREATE TABLE user_playlist_write (
    user INTEGER NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    playlist TEXT NOT NULL REFERENCES playlist(name) ON DELETE CASCADE,
    UNIQUE(user, playlist)
) STRICT;

CREATE TABLE user_lastfm (
    user INTEGER NOT NULL UNIQUE PRIMARY KEY REFERENCES user(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    key TEXT NOT NULL
) STRICT;

CREATE TABLE user_webauthn (
    user INTEGER NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    public_key BLOB NOT NULL
) STRICT;

CREATE TABLE session (
    user INTEGER NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    token TEXT NOT NULL UNIQUE,
    csrf_token TEXT NOT NULL,
    creation_date INTEGER NOT NULL, -- Seconds since UNIX epoch
    user_agent TEXT NULL,
    remote_address TEXT NULL,
    last_use INTEGER NOT NULL -- Seconds since UNIX epoch
) STRICT;

CREATE INDEX idx_session_user ON session(user);

CREATE TABLE history (
    timestamp INTEGER NOT NULL, -- Seconds since UNIX epoch
    user INTEGER NOT NULL, -- Intentionally not a foreign key, so history remains when user is deleted
    track TEXT NOT NULL, -- Intentionally not a foreign key, so history remains when user is deleted
    playlist TEXT NOT NULL, -- Could be obtained from track info, but included separately so it is remembered for deleted tracks or playlists
    private INTEGER NOT NULL -- 1 if entry must be hidden from history, only to be included in aggregated data
) STRICT;

CREATE INDEX idx_history_track_timestamp ON history(track, timestamp);

CREATE TABLE scanner_log (
    id INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL, -- Seconds since UNIX epoch
    action TEXT NOT NULL, -- Literal string 'insert', 'delete', or 'update'
    playlist TEXT NOT NULL, -- Intentionally not a foreign key, log may contain deleted playlists. Can be derived from track path, but stored for fast and easy lookup
    track TEXT NOT NULL,  -- Intentionally not a foreign key, log may contain deleted tracks
    user INTEGER NULL REFERENCES user(id) ON DELETE SET NULL
) STRICT;

CREATE INDEX idx_scanner_log_timestamp ON scanner_log(timestamp);

CREATE TABLE dislikes (
    user INTEGER NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    track TEXT NOT NULL REFERENCES track(path) ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE(user, track)
) STRICT;

CREATE TABLE share (
    share_code TEXT NOT NULL UNIQUE PRIMARY KEY,
    user INTEGER NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    create_timestamp INTEGER NOT NULL
) STRICT;

CREATE TABLE share_track (
    share_code TEXT NOT NULL REFERENCES share(share_code) ON DELETE CASCADE,
    track_code TEXT NOT NULL,
    track TEXT NOT NULL REFERENCES track(path) ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE(share_code, track_code)
) STRICT;

CREATE VIRTUAL TABLE track_fts USING fts5 (
    path,
    title,
    album,
    album_artist,
    artists,
    lyrics,
    tokenize='trigram case_sensitive 0 remove_diacritics 1', -- https://sqlite.org/fts5.html#the_trigram_tokenizer
    content='', -- https://www.sqlite.org/fts5.html#external_content_and_contentless_tables
    contentless_delete=1
);

CREATE TABLE blob (
    id TEXT NOT NULL UNIQUE,
    blobtype TEXT NOT NULL,
    track TEXT REFERENCES track(path) ON DELETE SET NULL ON UPDATE CASCADE,
    timestamp INTEGER NOT NULL,
    UNIQUE(blobtype, track)
) STRICT;

COMMIT;
