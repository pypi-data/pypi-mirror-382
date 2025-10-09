-- Fix artists column not initialized in update trigger
BEGIN;
DROP TRIGGER track_fts_update;
CREATE TRIGGER track_fts_update AFTER UPDATE ON track BEGIN
    DELETE FROM track_fts WHERE path=old.path;
    INSERT INTO track_fts (path, title, album, album_artist, lyrics, artists) VALUES (new.path, new.title, new.album, new.album_artist, new.lyrics, (SELECT GROUP_CONCAT(artist, ' ') FROM track_artist WHERE track = new.path));
END;
COMMIT;
