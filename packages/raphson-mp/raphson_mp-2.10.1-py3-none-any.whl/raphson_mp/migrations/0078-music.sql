-- add index to speed up query:
-- CREATE INDEX idx_track_playlist_duration ON track(playlist, duration);
CREATE INDEX idx_track_playlist_duration ON track(playlist, duration);
