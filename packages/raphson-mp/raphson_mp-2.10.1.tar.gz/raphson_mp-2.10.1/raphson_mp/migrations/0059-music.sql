PRAGMA foreign_keys=OFF;
BEGIN;

ALTER TABLE playlist RENAME COLUMN path TO name;

COMMIT;
