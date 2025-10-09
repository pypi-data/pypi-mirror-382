BEGIN;
-- These indices may have disappeared since migration 0029
CREATE INDEX IF NOT EXISTS idx_track_last_chosen ON track(last_chosen);
CREATE INDEX IF NOT EXISTS idx_track_playlist ON track(playlist);
COMMIT;
