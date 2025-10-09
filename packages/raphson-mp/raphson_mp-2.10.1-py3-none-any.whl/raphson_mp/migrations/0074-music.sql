-- Migrate track_fts table to contentless_delete
BEGIN;

DROP TRIGGER track_fts_insert;
DROP TRIGGER track_fts_delete;
DROP TRIGGER track_fts_update;

DROP TRIGGER track_fts_artist_insert;
DROP TRIGGER track_fts_artist_delete;
DROP TRIGGER track_fts_artist_update;

DROP TABLE track_fts;

CREATE VIRTUAL TABLE track_fts USING fts5 (
    path,
    title,
    album,
    album_artist,
    artists,
    lyrics,
    tokenize='unicode61 remove_diacritics 2', -- https://sqlite.org/fts5.html#unicode61_tokenizer
    content='', -- https://www.sqlite.org/fts5.html#external_content_and_contentless_tables
    contentless_delete=1
);

INSERT INTO track_fts (rowid, path, title, album, album_artist, lyrics, artists)
    SELECT track.rowid, path, title, album, album_artist, lyrics, GROUP_CONCAT(artist, ' ') FROM track LEFT JOIN track_artist ON path = track GROUP BY path;

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
        WHERE rowid = new.rowid;
END;

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

COMMIT;
