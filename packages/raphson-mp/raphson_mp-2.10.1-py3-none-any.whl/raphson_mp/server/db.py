import asyncio
import logging
import os
import re
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from sqlite3 import Connection, DatabaseError
from typing import NotRequired, TypedDict

from raphson_mp.common import const
from raphson_mp.server import settings

log = logging.getLogger(__name__)


def _new_connection(path: Path, read_only: bool = False) -> Connection:
    db_uri = f"file:{path.as_posix()}"
    if read_only:
        db_uri += "?mode=ro"

    conn = sqlite3.connect(db_uri, uri=True, timeout=30.0)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA temp_store = MEMORY")  # https://www.sqlite.org/pragma.html#pragma_temp_store
    conn.execute("PRAGMA synchronous = NORMAL")  # https://www.sqlite.org/pragma.html#pragma_synchronous

    return conn


class ConnectOptions(TypedDict):
    read_only: NotRequired[bool]
    should_exist: NotRequired[bool]


class Database:
    name: str
    conn: Connection | None = None

    def __init__(self, db_name: str):
        self.name = db_name

    @property
    def path(self):
        return Path(settings.data_dir, self.name + ".db")

    @contextmanager
    def connect(self):
        assert self.path.is_file()
        conn = _new_connection(self.path)
        try:
            yield conn
        finally:
            conn.commit()
            conn.close()

    def size(self) -> int:
        return os.stat(self.path).st_size

    async def create(self, init_sql: str | None = None):
        assert not await asyncio.to_thread(self.path.is_file)
        conn = _new_connection(self.path)
        try:
            if init_sql is None:
                init_sql = Path(const.INIT_SQL_PATH, f"{self.name}.sql").read_text(encoding="utf-8")
            conn.executescript(
                f"""
                PRAGMA auto_vacuum = INCREMENTAL; -- must be set before any tables are created
                PRAGMA journal_mode = WAL; -- https://www.sqlite.org/wal.html
                {init_sql}
                ANALYZE;
                """
            )
        finally:
            conn.close()


MUSIC = Database("music")
CACHE = Database("cache")
OFFLINE = Database("offline")
META = Database("meta")

DATABASES = [MUSIC, CACHE, OFFLINE, META]
_BY_NAME = {db.name: db for db in DATABASES}


async def create_databases() -> None:
    """
    Initialize SQLite databases using SQL scripts
    """
    for db in DATABASES:
        log.debug("creating: %s", db.path.name)
        await db.create()

    with META.connect() as conn:
        migrations = get_migrations()
        assert migrations
        version = migrations[-1].to_version

        log.info("setting initial database version to %s", version)

        conn.execute("INSERT INTO db_version VALUES (?)", (version,))


@dataclass
class Migration:
    path: Path
    to_version: int
    db_name: str

    async def run(self) -> None:
        """Execute migration file"""
        content = self.path.read_text(encoding="utf-8")

        if self.db_name == "python":
            raise NotImplementedError()
            # exec(content)
        else:
            with _BY_NAME[self.db_name].connect() as conn:
                conn.executescript(content)
                conn.executescript("ANALYZE;")


def get_migrations() -> list[Migration]:
    migration_file_names = [path.name for path in const.MIGRATIONS_SQL_PATH.iterdir() if path.name.endswith(".sql")]

    migrations: list[Migration] = []

    for i, file_name in enumerate(sorted(migration_file_names)):
        match = re.match(r"^(\d{4})-(\w+)\.(\w+)$", file_name)
        if match is None:
            log.warning("ignoring migration file: %s", file_name)
            continue

        to_version, db_name, ext = match.groups()
        to_version = int(to_version)

        assert ext == ("py" if db_name == "python" else "sql")
        assert i + 1 == to_version, f"unexpected version: expected {i} got {to_version}"
        assert db_name == "python" or db_name in _BY_NAME, db_name

        path = Path(const.MIGRATIONS_SQL_PATH, file_name)
        migrations.append(Migration(path, to_version, db_name))

    return migrations


def get_version() -> str:
    with sqlite3.connect(":memory:") as conn:
        version = conn.execute("SELECT sqlite_version()").fetchone()[0]
    conn.close()
    return version


def optimize():
    log.info("optimizing databases")
    for db in DATABASES:
        with db.connect() as conn:
            # ----- optimize -----
            # https://www.sqlite.org/pragma.html#pragma_optimize

            # ----- wal_checkpoint -----
            # Clean up wal/shm files, without blocking. Can only clean up parts of the WAL file that were written
            # before any reader has opened a connection.
            # > PASSIVE: Checkpoint as many frames as possible without waiting for any database readers or writers to
            # > finish.
            # https://www.sqlite.org/pragma.html#pragma_wal_checkpoint
            #
            # > A checkpoint operation takes content from the WAL file and transfers it back into the original database
            # > file. A checkpoint can run concurrently with readers, however the checkpoint must stop when it reaches
            # > a page in the WAL that is past the end mark of any current reader. The checkpoint has to stop at that
            # > point because otherwise it might overwrite part of the database file that the reader is actively using.
            # > The checkpoint remembers (in the wal-index) how far it got and will resume transferring content from
            # > the WAL to the database from where it left off on the next invocation.
            # >
            # > Thus a long-running read transaction can prevent a checkpointer from making progress. But presumably
            # > every read transaction will eventually end and the checkpointer will be able to continue.
            # https://www.sqlite.org/wal.html

            # ----- incremental_vacuum -----
            # Unmap deleted pages. The number of vacuumed pages is limited to prevent this function from blocking for
            # too long. With 4k pages, max 65536 pages for max 256MiB.

            conn.executescript(
                """
                PRAGMA optimize=0x10002;
                PRAGMA wal_checkpoint(TRUNCATE);
                PRAGMA incremental_vacuum(65536);
                """
            )


async def migrate() -> None:
    log.debug("using SQLite version: %s", get_version())

    if not (settings.data_dir / "meta.db").exists():
        log.info("creating databases")
        await create_databases()
        return

    with META.connect() as conn:
        version_row = conn.execute("SELECT version FROM db_version").fetchone()
        if version_row:
            version = version_row[0]
        else:
            raise DatabaseError("Version missing from database. Cannot continue.")

    migrations = get_migrations()

    if len(migrations) < version:
        raise DatabaseError("Database version is greater than number of migration files")

    pending_migrations = migrations[version:]
    if len(pending_migrations) == 0:
        log.debug("no pending migrations")
    else:
        for migration in pending_migrations:
            log.info("running migration to version %s", migration.to_version)
            await migration.run()
            with META.connect() as conn:
                conn.execute("UPDATE db_version SET version=?", (migration.to_version,))
