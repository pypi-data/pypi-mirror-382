-- Fix track column having a NOT NULL constraint while simultaneously having ON DELETE SET NULL
PRAGMA foreign_keys=OFF;
BEGIN;

CREATE TABLE blob_new (
    id TEXT NOT NULL,
    blobtype TEXT NOT NULL,
    track TEXT REFERENCES track(path) ON DELETE SET NULL ON UPDATE CASCADE,
    timestamp INTEGER NOT NULL
) STRICT;

INSERT INTO blob_new SELECT * FROM blob;

DROP TABLE blob;

ALTER TABLE blob_new RENAME TO blob;
COMMIT;
