PRAGMA foreign_keys=OFF;
BEGIN;

CREATE TABLE history_new (
    timestamp INTEGER NOT NULL, -- Seconds since UNIX epoch
    user INTEGER NOT NULL, -- Intentionally not a foreign key, so history remains when user is deleted
    track TEXT NOT NULL, -- Intentionally not a foreign key, so history remains when user is deleted
    playlist TEXT NOT NULL, -- Could be obtained from track info, but included separately so it is remembered for deleted tracks or playlists
    private INTEGER NOT NULL -- 1 if entry must be hidden from history, only to be included in aggregated data
) STRICT;

INSERT OR IGNORE INTO history_new SELECT timestamp, user, track, playlist, private FROM history;

DROP TABLE history;

ALTER TABLE history_new RENAME TO history;

CREATE INDEX idx_history_track_timestamp ON history(track, timestamp);

COMMIT;
