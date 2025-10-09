import functools
import logging

from aiohttp import web
from aiohttp.typedefs import Handler

from raphson_mp.routes import control
from raphson_mp.server import activity, db
from raphson_mp.server.decorators import simple_route

try:
    import prometheus_client
except ImportError:
    prometheus_client = None


_LOGGER = logging.getLogger(__name__)


@simple_route("")
async def route_metrics(_request: web.Request):
    if prometheus_client:
        return web.Response(body=prometheus_client.generate_latest(), content_type="text/plain")
    else:
        _LOGGER.warning("/metrics was queried, but it is unavailable because prometheus_client is not installed")
        raise web.HTTPServiceUnavailable()


if prometheus_client:

    # Database size
    g_database_size = prometheus_client.Gauge(
        "database_size", "Size of SQLite database files", labelnames=("database",)
    )
    for db in db.DATABASES:
        g_database_size.labels(db.name).set_function(db.size)

    # Active players
    g_players = prometheus_client.Gauge("players", "Players", labelnames=("state",))
    g_players.labels("Playing").set_function(
        lambda: sum(1 for playing in activity.now_playing() if not playing.data.paused)
    )
    g_players.labels("Paused").set_function(lambda: sum(1 for playing in activity.now_playing() if playing.data.paused))

    ALL_CATEGORIES: set[str] = {"File manager", "Subsonic", "Monitoring", "Error reporting", "WebDAV", "Other"}
    REQUEST_COUNTER: dict[str, int] = {category: 0 for category in ALL_CATEGORIES}
    ALL_STATUS: set[int] = {101, 200, 204, 207, 303, 400, 403, 500, 523, 0}
    RESPONSE_STATUS_COUNTER: dict[int, int] = {status: 0 for status in ALL_STATUS}

    def _request_category(request: web.Request) -> str:
        url = str(request.rel_url)
        if url.startswith("/files"):
            return "File manager"
        elif url.startswith("/rest"):
            return "Subsonic"
        elif url == "/metrics" or url == "/health_check":
            return "Monitoring"
        elif url == "/report_error" or url == "/csp_reports":
            return "Error reporting"
        elif url.startswith("/dav"):
            return "WebDAV"
        else:
            return "Other"

    @web.middleware
    async def request_counter(request: web.Request, handler: Handler) -> web.StreamResponse:
        response = await handler(request)

        # wrap in try-except so we don't break the entire application if there's a bug (like KeyError)
        try:
            REQUEST_COUNTER[_request_category(request)] += 1

            if response.status in RESPONSE_STATUS_COUNTER:
                RESPONSE_STATUS_COUNTER[response.status] += 1
            else:
                _LOGGER.warning("untracked response code %s", response.status)
                RESPONSE_STATUS_COUNTER[0] += 1
        except Exception:
            _LOGGER.error("error in request_counter", exc_info=True)

        return response

    g_request_category = prometheus_client.Gauge("request_category", "Requests", labelnames=("category",))
    for category in ALL_CATEGORIES:
        g_request_category.labels(category).set_function(functools.partial(REQUEST_COUNTER.get, category, 0))

    g_response_status = prometheus_client.Gauge("response_status", "Response HTTP status codes", labelnames=("status",))
    for status in ALL_STATUS:
        g_response_status.labels(status).set_function(functools.partial(RESPONSE_STATUS_COUNTER.get, status, 0))

    prometheus_client.Gauge("websocket_received", "Number of received websocket messages").set_function(
        lambda: control.received_message_counter
    )

else:

    @web.middleware
    async def request_counter(request: web.Request, handler: Handler) -> web.StreamResponse:
        return await handler(request)
