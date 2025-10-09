-- switch to trigram tokenizer
DROP TABLE track_fts;

CREATE VIRTUAL TABLE track_fts USING fts5 (
    path,
    title,
    album,
    album_artist,
    artists,
    lyrics,
    tokenize='trigram case_sensitive 0 remove_diacritics 1', -- https://sqlite.org/fts5.html#the_trigram_tokenizer
    content='', -- https://www.sqlite.org/fts5.html#external_content_and_contentless_tables
    contentless_delete=1
);

INSERT INTO track_fts (rowid, path, title, album, album_artist, lyrics, artists)
    SELECT track.rowid, path, title, album, album_artist, lyrics, GROUP_CONCAT(artist, ' ') FROM track LEFT JOIN track_artist ON path = track GROUP BY path;
