-- Add ctime column to track table
PRAGMA foreign_keys=OFF;

BEGIN;

CREATE TABLE track_new (
    path TEXT NOT NULL UNIQUE PRIMARY KEY,
    playlist TEXT NOT NULL REFERENCES playlist(path) ON DELETE CASCADE,
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

INSERT INTO track_new SELECT path, playlist, duration, title, album, album_artist, track_number, year, mtime, mtime, last_chosen, lyrics, video FROM track;

DROP TABLE track;

ALTER TABLE track_new RENAME TO track;

-- recreate indices

CREATE INDEX idx_track_playlist ON track(playlist);
CREATE INDEX idx_track_album ON track(album);
CREATE INDEX idx_track_album_artist ON track(album_artist);
CREATE INDEX idx_track_year ON track(year);
CREATE INDEX idx_track_last_chosen ON track(last_chosen);

-- recreate triggers

CREATE TRIGGER track_fts_insert AFTER INSERT ON track BEGIN
    INSERT INTO track_fts (path, title, album, album_artist) VALUES (new.path, new.title, new.album, new.album_artist);
END;

CREATE TRIGGER track_fts_delete AFTER DELETE ON track BEGIN
    DELETE FROM track_fts WHERE path=old.path;
END;

CREATE TRIGGER track_fts_update AFTER UPDATE ON track BEGIN
    UPDATE track_fts SET title = new.title, album = new.album, album_artist = new.album_artist WHERE path = new.path;
END;

COMMIT;
