-- Set tracks with empty lyrics to NULL, so the lyrics system will find lyrics for them.
-- For future tracks, the metadata scanner will ignore empty lyrics.
UPDATE track SET lyrics = NULL WHERE lyrics = '';
