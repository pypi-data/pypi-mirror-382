PYTHON=.venv/bin/python
PYBABEL=$(PYTHON) -m babel.messages.frontend
MUSIC=.venv/bin/raphson-mp

.PHONY: clean run-offline test testall update-messages compile-messages deploy-container format spellcheck release

$(PYTHON):
	python3 -m venv .venv

$(MUSIC): $(PYTHON) pyproject.toml
	$(PYTHON) -m pip install --editable .[full,dev]

clean:
	rm -rf .pytest-cache dist messages.pot

run: compile-messages
	$(MUSIC) --log-level DEBUG --bwrap start --access-log --dev

run-offline:
	$(MUSIC) --log-level DEBUG --data-dir data-offline --offline start --access-log --dev

test: $(MUSIC)
	$(PYTHON) -m pytest -m "not online"

testall: $(MUSIC)
	$(PYTHON) -m coverage run -m pytest

coverage: $(MUSIC)
	$(PYTHON) -m coverage report

update-messages: $(MUSIC)
	$(PYBABEL) extract --mapping babel.cfg --keyword gettext_lazy --output messages.pot raphson_mp
	$(PYBABEL) update -i messages.pot -d raphson_mp/translations

compile-messages: $(MUSIC)
	$(PYBABEL) compile -d raphson_mp/translations

deploy-container: clean
	podman build -t codeberg.org/raphson/music-server --target prod .
	podman build -f Containerfile.nginx -t codeberg.org/raphson/music-server-nginx .
	podman push codeberg.org/raphson/music-server
	podman push codeberg.org/raphson/music-server-nginx

format: $(MUSIC)
	$(PYTHON) -m black .
	$(PYTHON) -m isort .

spellcheck:
	codespell --builtin clear,rare,informal,usage --skip './data/*,./raphson_mp/translations/*,./raphson_mp/static/lib/*,./tests/data/*'

release:
	$(PYTHON) release.py
