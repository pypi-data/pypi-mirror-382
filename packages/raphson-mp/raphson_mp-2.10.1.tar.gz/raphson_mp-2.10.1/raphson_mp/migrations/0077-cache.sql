-- delete legacy, now unused, cache entries
DELETE FROM cache WHERE
    key LIKE 'genius%' OR
    key LIKE 'loud%' OR
    key LIKE 'lyrics%' OR
    key LIKE 'spotify_artist_image%';
