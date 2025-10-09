-- allow password to be null

PRAGMA foreign_keys=OFF;

BEGIN;

CREATE TABLE user_new (
    id INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    nickname TEXT NULL,
    password TEXT NULL,
    admin INTEGER NOT NULL DEFAULT 0,
    primary_playlist TEXT NULL REFERENCES playlist(path) ON DELETE SET NULL,
    language TEXT NULL,
    privacy TEXT NULL,
    theme TEXT NOT NULL DEFAULT 'default'
) STRICT;

INSERT INTO user_new SELECT * FROM user;

DROP TABLE user;

ALTER TABLE user_new RENAME TO user;

COMMIT;
