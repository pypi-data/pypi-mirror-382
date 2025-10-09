BEGIN;

CREATE INDEX idx_track_artist_track ON track_artist(track);
CREATE INDEX idx_track_artist_artist ON track_artist(artist);

CREATE INDEX idx_track_tag_track ON track_tag(track);
CREATE INDEX idx_track_tag_tag ON track_tag(tag);

COMMIT;
