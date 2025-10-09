-- expire all audio cache entries
-- expired entries will slowly be deleted by the server during maintenance
UPDATE cache SET expire_time = 0 WHERE key LIKE 'audio%';
