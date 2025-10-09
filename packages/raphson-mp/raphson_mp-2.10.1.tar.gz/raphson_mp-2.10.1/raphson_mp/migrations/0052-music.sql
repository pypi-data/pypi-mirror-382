-- Fix mistake in artist trigger causing data to be updated for ALL track_fts rows
PRAGMA foreign_keys = OFF;

BEGIN;

DROP TRIGGER track_fts_artist_insert;
DROP TRIGGER track_fts_artist_delete;
DROP TRIGGER track_fts_artist_update;

CREATE TRIGGER track_fts_artist_insert AFTER INSERT ON track_artist BEGIN
    UPDATE track_fts SET artists = (SELECT GROUP_CONCAT(artist, ' ') FROM track_artist WHERE track=new.track GROUP BY track) WHERE path=new.track;
END;

CREATE TRIGGER track_fts_artist_delete AFTER DELETE ON track_artist BEGIN
    UPDATE track_fts SET artists = (SELECT GROUP_CONCAT(artist, ' ') FROM track_artist WHERE track=old.track GROUP BY track) WHERE path=old.track;
END;

CREATE TRIGGER track_fts_artist_update AFTER UPDATE ON track_artist BEGIN
    UPDATE track_fts SET artists = (SELECT GROUP_CONCAT(artist, ' ') FROM track_artist WHERE track=new.track GROUP BY track) WHERE path=old.track;
END;

-- Fix wrong content
DELETE FROM track_fts;
INSERT INTO track_fts SELECT path, title, album, album_artist, GROUP_CONCAT(artist, ' ') FROM track LEFT JOIN track_artist ON path = track GROUP BY path;

COMMIT;
