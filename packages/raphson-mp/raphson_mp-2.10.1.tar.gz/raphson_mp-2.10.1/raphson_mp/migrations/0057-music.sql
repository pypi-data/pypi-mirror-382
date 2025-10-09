-- allow changing track paths - add ON UPDATE CASCADE to foreign keys
PRAGMA foreign_keys=OFF;
BEGIN;

CREATE TABLE track_artist_new (
    track TEXT NOT NULL REFERENCES track(path) ON DELETE CASCADE ON UPDATE CASCADE,
    artist TEXT NOT NULL COLLATE NOCASE,
    UNIQUE (track, artist)
) STRICT;
INSERT INTO track_artist_new SELECT * FROM track_artist;
DROP TABLE track_artist;
ALTER TABLE track_artist_new RENAME TO track_artist;

CREATE INDEX idx_track_artist_track ON track_artist(track);
CREATE INDEX idx_track_artist_artist ON track_artist(artist);

CREATE TRIGGER track_fts_artist_insert AFTER INSERT ON track_artist BEGIN
    UPDATE track_fts SET artists = (SELECT GROUP_CONCAT(artist, ' ') FROM track_artist WHERE track=new.track GROUP BY track) WHERE path=new.track;
END;
CREATE TRIGGER track_fts_artist_delete AFTER DELETE ON track_artist BEGIN
    UPDATE track_fts SET artists = (SELECT GROUP_CONCAT(artist, ' ') FROM track_artist WHERE track=old.track GROUP BY track) WHERE path=old.track;
END;
CREATE TRIGGER track_fts_artist_update AFTER UPDATE ON track_artist BEGIN
    UPDATE track_fts SET artists = (SELECT GROUP_CONCAT(artist, ' ') FROM track_artist WHERE track=new.track GROUP BY track) WHERE path=old.track;
END;

CREATE TABLE track_tag_new (
    track TEXT NOT NULL REFERENCES track(path) ON DELETE CASCADE ON UPDATE CASCADE,
    tag TEXT NOT NULL COLLATE NOCASE,
    UNIQUE (track, tag)
) STRICT;
INSERT INTO track_tag_new SELECT * FROM track_tag;
DROP TABLE track_tag;
ALTER TABLE track_tag_new RENAME TO track_tag;

CREATE INDEX idx_track_tag_track ON track_tag(track);
CREATE INDEX idx_track_tag_tag ON track_tag(tag);

CREATE TABLE dislikes_new (
    user INTEGER NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    track TEXT NOT NULL REFERENCES track(path) ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE(user, track)
) STRICT;
INSERT INTO dislikes_new SELECT * FROM dislikes;
DROP TABLE dislikes;
ALTER TABLE dislikes_new RENAME TO dislikes;

CREATE TABLE shares_new (
    share_code TEXT NOT NULL UNIQUE PRIMARY KEY,
    user INTEGER NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    track TEXT NOT NULL REFERENCES track(path) ON DELETE CASCADE ON UPDATE CASCADE,
    create_timestamp INTEGER NOT NULL
) STRICT;
INSERT INTO shares_new SELECT * FROM shares;
DROP TABLE shares;
ALTER TABLE shares_new RENAME TO shares;

DROP TABLE radio_track;
CREATE TABLE radio_track (
    track TEXT NOT NULL REFERENCES track(path) ON DELETE CASCADE ON UPDATE CASCADE,
    start_time INTEGER NOT NULL
) STRICT;

COMMIT;
