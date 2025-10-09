-- allow multiple tracks per share
PRAGMA foreign_keys=OFF;
BEGIN;

CREATE TABLE share (
    share_code TEXT NOT NULL UNIQUE PRIMARY KEY,
    user INTEGER NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    create_timestamp INTEGER NOT NULL
) STRICT;

CREATE TABLE share_track (
    share_code TEXT NOT NULL REFERENCES share(share_code) ON DELETE CASCADE,
    track_code TEXT NOT NULL,
    track TEXT NOT NULL REFERENCES track(path) ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE(share_code, track_code)
) STRICT;

INSERT INTO share SELECT share_code, user, create_timestamp FROM shares;
INSERT INTO share_track SELECT share_code, share_code, track FROM shares;

DROP TABLE shares;

COMMIT;
