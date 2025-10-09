BEGIN;

DROP INDEX idx_track_playlist;
DROP INDEX idx_track_album;
DROP INDEX idx_track_album_artist;
DROP INDEX idx_track_year;

CREATE INDEX idx_track_filter ON track(path, playlist, title, album, album_artist, year, mtime, ctime);

COMMIT;
