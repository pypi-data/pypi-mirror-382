-- Add unique constraint to id and (blobtype, track)
PRAGMA foreign_keys=OFF;
BEGIN;

CREATE TABLE blob_new (
    id TEXT NOT NULL UNIQUE,
    blobtype TEXT NOT NULL,
    track TEXT REFERENCES track(path) ON DELETE SET NULL ON UPDATE CASCADE,
    timestamp INTEGER NOT NULL,
    UNIQUE(blobtype, track)
) STRICT;

-- simply ignore existing duplicates, the blob system is smart enough to make something sensible of missing data
INSERT OR IGNORE INTO blob_new SELECT * FROM blob;

DROP TABLE blob;

ALTER TABLE blob_new RENAME TO blob;
COMMIT;
