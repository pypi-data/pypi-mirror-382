CREATE TABLE track_loudness (
    track TEXT NOT NULL UNIQUE REFERENCES track(PATH) ON DELETE CASCADE ON UPDATE CASCADE,
    input_i REAL NOT NULL,
    input_tp REAL NOT NULL,
    input_lra REAL NOT NULL,
    input_thresh REAL NOT NULL,
    target_offset REAL NOT NULL
) STRICT;
