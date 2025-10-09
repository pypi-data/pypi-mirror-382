-- Fix ambiguous column rowid error in some sqlite versions
BEGIN;
DROP TRIGGER track_update;
CREATE TRIGGER track_update AFTER UPDATE ON track BEGIN
    UPDATE track_fts
        SET path = d.path, title = d.title, album = d.album, album_artist = d.album_artist, lyrics = d.lyrics, artists = d.artists
        FROM (SELECT path, title, album, album_artist, lyrics, GROUP_CONCAT(artist, ' ') AS artists FROM track JOIN track_artist ON path = track WHERE track.rowid = new.rowid GROUP BY path) AS d
        WHERE track_fts.rowid = new.rowid;
END;
COMMIT;
