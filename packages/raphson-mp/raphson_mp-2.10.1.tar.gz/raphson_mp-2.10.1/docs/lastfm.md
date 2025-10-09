# Last.fm integration

## Server setup

Create an API key on this page: https://www.last.fm/api/account/create

Callback URL should be set to `https://server/lastfm/callback`.

Set the `--lastfm-api-key` and `--lastfm-api-secret` options or `MUSIC_LASTFM_API_KEY` and `MUSIC_LASTFM_API_SECRET` environment variables.

Warning: If you change the api key, all users must link their last.fm account again.

## Link user account

Link your account to last.fm in music player account settings.
