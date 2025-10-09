-- In migration 0059, playlist(path) was renamed to playlist(name). However, foreign key references were not updated.
PRAGMA foreign_keys=OFF;
BEGIN;

CREATE TABLE user_new (
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

CREATE TABLE user_playlist_favorite_new (
    user INTEGER NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    playlist TEXT NOT NULL REFERENCES playlist(name) ON DELETE CASCADE,
    UNIQUE (user, playlist)
) STRICT;

CREATE TABLE user_playlist_write_new (
    user INTEGER NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    playlist TEXT NOT NULL REFERENCES playlist(name) ON DELETE CASCADE,
    UNIQUE(user, playlist)
) STRICT;

CREATE TABLE track_new (
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

INSERT INTO user_new SELECT * FROM user;
INSERT INTO user_playlist_favorite_new SELECT * FROM user_playlist_favorite;
INSERT INTO user_playlist_write_new SELECT * FROM user_playlist_write;
INSERT INTO track_new SELECT * FROM track;

DROP TABLE user;
DROP TABLE user_playlist_favorite;
DROP TABLE user_playlist_write;
DROP TABLE track;

ALTER TABLE user_new RENAME TO user;
ALTER TABLE user_playlist_favorite_new RENAME TO user_playlist_favorite;
ALTER TABLE user_playlist_write_new RENAME TO user_playlist_write;
ALTER TABLE track_new RENAME TO track;

-- Recreate deleted indices and triggers
CREATE INDEX idx_track_playlist ON track(playlist);
CREATE INDEX idx_track_album ON track(album);
CREATE INDEX idx_track_album_artist ON track(album_artist);
CREATE INDEX idx_track_year ON track(year);
CREATE INDEX idx_track_last_chosen ON track(last_chosen);

CREATE TRIGGER track_fts_insert AFTER INSERT ON track BEGIN
    INSERT INTO track_fts (path, title, album, album_artist) VALUES (new.path, new.title, new.album, new.album_artist);
END;

CREATE TRIGGER track_fts_delete AFTER DELETE ON track BEGIN
    DELETE FROM track_fts WHERE path=old.path;
END;

CREATE TRIGGER track_fts_update AFTER UPDATE ON track BEGIN
    UPDATE track_fts SET title = new.title, album = new.album, album_artist = new.album_artist WHERE path = new.path;
END;

-- The broken foreign key is likely what caused the bug seen in migration 0060, so the track_fts table is also repopulated.
DELETE FROM track_fts;
INSERT INTO track_fts SELECT path, title, album, album_artist, GROUP_CONCAT(artist, ' ') FROM track LEFT JOIN track_artist ON path = track GROUP BY path;

COMMIT;
