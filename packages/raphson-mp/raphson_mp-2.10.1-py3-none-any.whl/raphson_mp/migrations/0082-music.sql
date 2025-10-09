BEGIN;
DROP INDEX idx_history_timestamp;
DROP INDEX idx_history_user;
DROP INDEX idx_history_track;
DROP INDEX idx_history_private;
COMMIT;
