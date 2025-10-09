# Data

This is a technical explanation of files stored in the data directory.

## `blob`

Transcoded audio and video is stored in the blobs directory. An index to these files is stored in `music.db`. This directory will take up approximately 10-15GB of space for every 1000 tracks. You can exclude this directory from backups. If files go missing, the server will regenerate them.

## `cache`

From version 2.9.0, the `cache` directory is not used and should be deleted.

For older versions: The `cache` directory stores cache files that are very large and not stored in `cache.db` directly. Do NOT delete this directory. If you do accidentally delete this directory, run `sqlite3 cache.db 'DELETE FROM cache WHERE external = true;'` to remove references to deleted files.

## `errors.log`

This is a text file containing all log messages with a `WARNING` level or higher. After acknowledging the warnings, you may empty the file using `truncate -s 0 errors.log`. Log entries `WARNING` level signals a potential issue. At `ERROR` level, the log message probably indicates a bug. Creating an issue for these bugs would be appreciated!

## `music.db`

This is the main database. All important data is stored here, like accounts, settings, playback history, and an index of music files and metadata. It should not get larger than a few megabytes.

## `cache.db`

The cache database is used to store the result of expensive operations. For example, it stores loudness data and album cover images. It is normally not larger than 2GB per 1000 tracks.

This database, like other databases, must not be deleted. If you have accidentally deleted it, also delete the `cache` directory if it exists, and then create the database using the SQL commands in `raphson_mp/sql/cache.sql`.

The cache database is being phased out in favor of the "blobs" directory.

## `meta.db`

This database stores information about the database version, allowing the app to run the correct database migrations during an upgrade.

## `offline.db`

The offline database stores downloaded track data when the music player operates in [offline mode](./offline.md). It is **not** safe to delete this database.

## VACUUM database

If you experience performance issues, especially with cache.db, it may help to vacuum a database.

1. `sqlite3 cache.db "PRAGMA auto_vacuum = INCREMENTAL; VACUUM INTO 'cache.new.db';"`
2. `sqlite3 cache.new.db 'PRAGMA journal_mode = WAL;'`
3. Shut down the music server
4. `mv cache.db cache.old.db`
5. `mv cache.new.db cache.db`
6. Start the music server and let it run for a while to check for unexpected issues
7. `rm cache.old.db`
