from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as get_version
from pathlib import Path

try:
    PACKAGE_VERSION = get_version(__name__.split(".")[0])
except PackageNotFoundError:
    PACKAGE_VERSION = "dev"  # pyright: ignore[reportConstantRedefinition]

PACKAGE_PATH = Path(__file__).parent.parent.resolve()
STATIC_PATH = Path(PACKAGE_PATH, "static")
MIGRATIONS_SQL_PATH = Path(PACKAGE_PATH, "migrations")
INIT_SQL_PATH = Path(PACKAGE_PATH, "sql")
RAPHSON_PNG_PATH = Path(STATIC_PATH, "img", "raphson.png")

SERVER_MAINTENANCE_INTERVAL = 3600
