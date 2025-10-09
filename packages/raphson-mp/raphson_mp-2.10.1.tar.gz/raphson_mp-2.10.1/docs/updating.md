# Updating

Please check the release notes to see if there are any breaking changes.

## Pipx

```
pipx install --upgrade 'raphson-mp[online]'
```
or
```
pipx install --upgrade 'raphson-mp[offline]'
```

## Container

1. Enter the correct directory
2. Update the tag to the latest, if you are not using the :latest tag.
3. Run `docker compose pull` to download new images
4. Run `docker compose up -d` to recreate the containers

## Compatibility

* A new version is always compatible with data from an old version. Your database will be upgraded automatically. Downgrading is not possible when database migrations have been performed.
* The web UI from an older version may not work properly with a new server version. Upgrade your server while it is not in use to minimize disruptions. Bugfix releases are generally fine, but not larger releases.
* The server will try to keep compatibility with clients (like the offline music player) made for an older server version. Any issues experienced when connecting with an older, but still relatively recent, client to a new server should be considered a bug.
