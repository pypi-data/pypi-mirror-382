-- add lyrics to FTS table
BEGIN;

-- create new table
DROP TABLE track_fts;
CREATE VIRTUAL TABLE track_fts USING fts5 (
    path,
    title,
    album,
    album_artist,
    lyrics,
    artists,
    tokenize='unicode61 remove_diacritics 2' -- https://sqlite.org/fts5.html#unicode61_tokenizer
);

-- update triggers
DROP TRIGGER track_fts_insert;
CREATE TRIGGER track_fts_insert AFTER INSERT ON track BEGIN
    INSERT INTO track_fts (path, title, album, album_artist, lyrics) VALUES (new.path, new.title, new.album, new.album_artist, new.lyrics);
END;

DROP TRIGGER track_fts_update;
CREATE TRIGGER track_fts_update AFTER UPDATE ON track BEGIN
    DELETE FROM track_fts WHERE path=old.path;
    INSERT INTO track_fts (path, title, album, album_artist, lyrics) VALUES (new.path, new.title, new.album, new.album_artist, new.lyrics);
END;

-- repopulate with data
INSERT INTO track_fts SELECT path, title, album, album_artist, lyrics, GROUP_CONCAT(artist, ' ') FROM track LEFT JOIN track_artist ON path = track GROUP BY path;

COMMIT;
