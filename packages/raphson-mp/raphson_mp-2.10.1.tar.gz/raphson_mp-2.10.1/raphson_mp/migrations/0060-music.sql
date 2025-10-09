-- There seemed to be a bug that caused orphan entries in track_fts
-- This became apparent when track_fts was no longer queried using an inner join with track
-- Assuming the bug is solved, simply re-populate the track_fts

DELETE FROM track_fts;
INSERT INTO track_fts SELECT path, title, album, album_artist, GROUP_CONCAT(artist, ' ') FROM track LEFT JOIN track_artist ON path = track GROUP BY path;
