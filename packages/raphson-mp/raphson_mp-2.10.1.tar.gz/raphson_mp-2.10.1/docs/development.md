# Development

```
make run
```

This command will create a venv, install the necessary packages, and finally start the server in development mode.

The module is installed as an [editable installation](https://setuptools.pypa.io/en/latest/userguide/development_mode.html). It can be run manually by entering the venv and running `python3 -m raphson-mp`

To test the music player in offline mode (music synced from another server), use: `make run-offline`

## Development tools

You should install these utilities for a fully functional development environment:
```
sudo dnf install podman codespell sqldiff
```

## Development using containers

With `docker` and `docker-compose-plugin` installed, run the following command to start a local testing server:
```
docker compose up --build
```

You may need to change `user` in the `compose.yaml` file if your user is not using the default id of 1000.

## Code structure

  * (`data/`): default database directory.
  * `container/`: additional files used to build containers.
  * `debian/`: files used to build deb packages.
  * `docs/`: documentation in markdown format.
  * (`music/`): default music directory.
  * `raphson_mp/`: contains program source code
    * `client/`: helpers for client applications
    * `common/`: shared data structures for both the server and clients
    * `migrations/`: sql files used to update the database.
    * `routes`: files containing route functions (marked with `@route`)
    * `sql/`: sql files used to initialize the database, also useful as a database layout reference.
    * `static/`: static files that are served as-is by the frontend, under the `/static` URL.
    * `templates/`: jinja2 template files for web pages.
    * `translations/`: translation files, see translations section.

## Code style

Use `make format` to ensure proper code style. `pyproject.toml` contains some settings which should be picked up automatically.

## Preparing for development while offline

### Container images

If you wish to use Docker for development, use `docker pull` to download the base image (first line of Dockerfile). If you don't do this, buildx will attempt to pull the image very frequently while rebuilding, which won't work offline.

Then, build and start the container: `docker compose up --build`. Following builds will be cached, unless you change one of the `RUN` instructions in the `Dockerfile`.

### Music

Add some music to `./music`. Adding only a small amount is recommended. While online, start the web interface, enable all playlists and skip through all tracks. This will ensure album art and lyrics are downloaded to the cache for all tracks.

## Translations

### For developers

In templates:
```jinja
{% trans %}Something in English{% endtrans %}
{{ gettext('Something in English') }}
```

In Python:
```py
from i18n import gettext

translated_string = gettext('Something in English')
```

### For translators

1. Run `make update-messages`
2. Edit the `messages.po` file in `raphson_mp/translations/<language_code>/LC_MESSAGES/` using a text editor or PO editor like Poedit. To create a new language, run: `pybabel init -i messages.pot -d raphson_mp/translations -l <language_code>`
3. Run `make update-messages` again to ensure the language files are in a consistent format, regardless of your PO editor.
4. To actually see your changes, run `make compile-messages` and restart the server.

## Testing

Run all tests, except for online tests: `make test`

Run all tests: `make testall`

⚠️ Do not run all tests too often. Web scraping can trigger rate limits, especially in the case of automated tests which make the same requests every time.

Run a specific test: `pytest tests/test_server.py`

Measure code coverage:
```
make testall
make coverage
```

Test coverage history:

| Date       | Total code coverage | Number of tests
| ---------- | ------------------- | ---------------
| 2024-12-05 | 48%                 |
| 2024-12-09 | 54%                 |
| 2024-12-11 | 56%                 |
| 2024-12-13 | 60%                 |
| 2024-12-21 | 61%                 |
| 2024-12-24 | 63%                 |
| 2025-01-18 | 62%                 |
| 2025-02-18 | 66%                 |
| 2025-02-21 | 71%                 |
| 2025-03-12 | 73%                 |
| 2025-05-22 | 73%                 |
| 2025-06-14 | 71%                 |
| 2025-06-16 | 76%                 |
| 2025-06-18 | 78%                 | 140
| 2025-08-04 | 80%                 | 156

## Release

* Run tests: `make testall`
* Update version in `pyproject.toml`
* Update changelog in `CHANGES.md`
* Deploy to PyPi: `make deploy-pypi`
* Deploy to Docker Hub: `make deploy-container`
* ~~Update Debian changelog (`debian/changelog`). Get the date using `date -R`~~
* ~~Build new Debian package and upload it to the repo (manually for now)~~
* Commit and create a tag
