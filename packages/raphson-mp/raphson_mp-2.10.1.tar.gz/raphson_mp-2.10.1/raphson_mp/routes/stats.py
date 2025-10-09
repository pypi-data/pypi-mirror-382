from sqlite3 import Connection

from aiohttp import web

from raphson_mp.server import charts
from raphson_mp.server.auth import User
from raphson_mp.server.charts import StatsPeriod
from raphson_mp.server.decorators import route
from raphson_mp.server.response import template


@route("", redirect_to_login=True)
async def route_stats(_request: web.Request, conn: Connection, _user: User):
    years = [
        row[0]
        for row in conn.execute("SELECT DISTINCT strftime('%Y', timestamp, 'unixepoch', 'localtime') FROM history")
    ]
    return await template("stats.jinja2", years=years, chart_count=len(charts.CHARTS))


@route("/data/{chart}")
async def route_stats_data(request: web.Request, _conn: Connection, _user: User):
    try:
        period = StatsPeriod.from_name(request.query["period"])

    except ValueError:
        raise web.HTTPBadRequest(reason="invalid period")
    chart_id = int(request.match_info["chart"])
    data = await charts.get_chart(chart_id, period)
    if data is None:
        raise web.HTTPNoContent(reason="not enough data")
    return web.json_response(data)
