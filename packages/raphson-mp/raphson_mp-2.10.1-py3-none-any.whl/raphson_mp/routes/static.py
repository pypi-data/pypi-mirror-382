from aiohttp import web

from raphson_mp.common import const
from raphson_mp.server.decorators import Route

static = Route([web.static("/", const.STATIC_PATH)])
