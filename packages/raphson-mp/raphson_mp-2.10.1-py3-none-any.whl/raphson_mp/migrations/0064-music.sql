-- The track_fts_update trigger did not correctly handle tracks being moved (path being changed).
-- Repopulate the track_fts table to remove any invalid rows.

DROP TRIGGER track_fts_update;

CREATE TRIGGER track_fts_update AFTER UPDATE ON track BEGIN
    DELETE FROM track_fts WHERE path=old.path;
    INSERT INTO track_fts (path, title, album, album_artist) VALUES (new.path, new.title, new.album, new.album_artist);
END;

DELETE FROM track_fts;
INSERT INTO track_fts SELECT path, title, album, album_artist, GROUP_CONCAT(artist, ' ') FROM track LEFT JOIN track_artist ON path = track GROUP BY path;
