import os
from sqlite3 import Connection

from aiohttp import web

from raphson_mp.server import auth, logconfig
from raphson_mp.server.decorators import route
from raphson_mp.server.i18n import gettext
from raphson_mp.server.response import template


MAX_LOG_SIZE = 128*1024


@route("", require_admin=True)
async def view(_request: web.Request, _conn: Connection, _user: auth.User):
    logfile_path = logconfig.error_logfile_path()
    if logfile_path.is_file():
        with logfile_path.open("rb") as fp:
            fp.seek(0, os.SEEK_END)
            size = fp.tell()
            if size == 0:
                error = gettext("Log file is empty")
                log_content = None
            elif size > MAX_LOG_SIZE:
                error = gettext("Log file is too large, displaying only a section from the end.")
                fp.seek(-MAX_LOG_SIZE, os.SEEK_END)
                raw_log_content = fp.read()
                # show log starting at first full line
                log_content = raw_log_content[raw_log_content.index(b'\n')+1:].decode()
            else:
                fp.seek(0)
                error = None
                log_content = fp.read().decode()
    else:
        error = gettext("Log file does not exist")
        log_content = None

    return await template("log.jinja2", log_content=log_content, error=error)


@route("/clear", require_admin=True)
async def clear(_request: web.Request, _conn: Connection, _user: auth.User):
    os.truncate(logconfig.error_logfile_path(), 0)
    return web.HTTPSeeOther("/log")
