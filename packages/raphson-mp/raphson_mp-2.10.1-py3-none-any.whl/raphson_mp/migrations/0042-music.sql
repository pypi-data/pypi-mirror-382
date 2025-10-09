-- Remove unnecessary indices
BEGIN;
DROP INDEX IF EXISTS idx_track_artist_track;
DROP INDEX IF EXISTS idx_track_tag_track;
COMMIT;
