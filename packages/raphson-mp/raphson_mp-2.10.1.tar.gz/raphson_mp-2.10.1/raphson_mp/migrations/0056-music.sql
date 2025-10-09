-- allow multiple webauthn keys per user
PRAGMA foreign_keys=OFF;
BEGIN;
CREATE TABLE user_webauthn_new (
    user INTEGER NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    public_key BLOB NOT NULL
) STRICT;
INSERT INTO user_webauthn_new SELECT * FROM user_webauthn;
DROP TABLE user_webauthn;
ALTER TABLE user_webauthn_new RENAME TO user_webauthn;
COMMIT;
