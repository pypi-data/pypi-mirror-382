import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from sqlite3 import Connection
from typing import NotRequired, TypedDict, cast

from typing_extensions import override

from raphson_mp.server import cache, db
from raphson_mp.server.i18n import gettext as _

LegendDataT = list[str]
DataT = list[int]
MultiDataT = dict[str, DataT]
SeriesT = list[dict[str, str | list[int]]]
HeatmapDataT = list[tuple[int, int, float]]
HeatmapSeriesT = list[dict[str, str | HeatmapDataT]]


class ChartTitle(TypedDict):
    text: NotRequired[str]


class ChartAxisLabel(TypedDict):
    interval: NotRequired[int]


class ChartSplitLine(TypedDict):
    show: NotRequired[bool]


class ChartAxis(TypedDict):
    type: str
    data: list[str] | list[int] | None
    name: str
    splitLine: NotRequired[ChartSplitLine]
    inverse: NotRequired[bool]
    axisLabel: NotRequired[ChartAxisLabel]


class ChartLegend(TypedDict):
    orient: str
    right: int
    top: str
    type: str
    data: LegendDataT


class ChartVisualMap(TypedDict):
    min: float
    max: float
    orient: str
    right: int | str
    top: int | str


class Chart(TypedDict):
    title: ChartTitle
    xAxis: ChartAxis
    yAxis: ChartAxis
    series: SeriesT | HeatmapSeriesT
    legend: NotRequired[ChartLegend]
    visualMap: NotRequired[ChartVisualMap]


_LOGGER = logging.getLogger(__name__)


@dataclass
class StatsPeriod:
    start: int
    end: int

    @override
    def __str__(self):
        return f"StatsPeriod[{datetime.fromtimestamp(self.start).isoformat()} - {datetime.fromtimestamp(self.end).isoformat()}]"

    @property
    def query_where(self):
        return f"timestamp > {self.start} AND timestamp < {self.end}"

    @classmethod
    def from_name(cls, period: str):
        now_dt = datetime.now()
        now = now_dt.timestamp()
        start = 0
        end = now

        if period == "day":
            start = now - 60 * 60 * 24
        elif period == "week":
            start = now - 60 * 60 * 24 * 7
        elif period == "this_month":
            start = datetime(now_dt.year, now_dt.month, 1).timestamp()
        elif period == "last_month":
            month = (now_dt.month - 2) % 12 + 1
            month_year = now_dt.year - 1 if month == 12 else now_dt.year
            start = datetime(month_year, month, 1).timestamp()
            end = datetime(now_dt.year, now_dt.month, day=1).timestamp()
        elif period == "all":
            pass
        else:
            # period is a year
            year = int(period)
            start = datetime(year, 1, 1).timestamp()
            end = datetime(year + 1, 1, 1).timestamp()

        return cls(int(start), int(end))


def chart(
    title: str,
    ldata: LegendDataT | None,
    xdata: list[str] | list[int] | None,
    ydata: list[str] | list[int] | None,
    series: SeriesT | HeatmapSeriesT,
    xname: str,
    yname: str,
    all_labels: bool = False,
) -> Chart:
    assert xdata is not None or ydata is not None
    chart: Chart = {
        "title": {"text": title},
        "xAxis": {
            "type": "category" if xdata else "value",
            "data": xdata,
            "name": xname,
            "splitLine": {
                "show": False,
            },
        },
        "yAxis": {
            "type": "category" if ydata else "value",
            "data": ydata,
            "name": yname,
            "splitLine": {
                "show": False,
            },
            "inverse": ydata is not None and xdata is None,
        },
        "series": series,
    }

    if all_labels:
        for axis in ("xAxis", "yAxis"):
            chart[axis]["axisLabel"] = {"interval": 0}

    if ldata:
        chart["legend"] = {
            "orient": "vertical",
            "right": 0,
            "top": "center",
            "type": "scroll",
            "data": ldata,
        }

    return chart


def bar(
    title: str,
    axisdata: list[str] | list[int],
    seriesdata: DataT,
    xname: str,
    yname: str,
    horizontal: bool = False,
    all_labels: bool = False,
) -> Chart:
    series = [{"type": "bar", "data": seriesdata}]
    xdata = axisdata if not horizontal else None
    ydata = axisdata if horizontal else None
    return chart(title, None, xdata, ydata, series, xname, yname, all_labels=all_labels)


def multibar(
    title: str,
    axisdata: list[str] | list[int],
    seriesdata: MultiDataT,
    xname: str,
    yname: str,
    horizontal: bool = False,
    all_labels: bool = False,
) -> Chart | None:
    if not seriesdata:
        return None
    series = [{"name": name, "type": "bar", "stack": "x", "data": data} for name, data in seriesdata.items()]
    ldata = [name for name, _ in seriesdata.items()]
    xdata = axisdata if not horizontal else None
    ydata = axisdata if horizontal else None
    return chart(title, ldata, xdata, ydata, series, xname, yname, all_labels=all_labels)


def heatmap(
    title: str,
    name: str,
    xdata: LegendDataT,
    ydata: LegendDataT,
    seriesdata: HeatmapDataT,
    xname: str,
    yname: str,
) -> Chart:
    series = [{"name": name, "type": "heatmap", "data": seriesdata}]
    c = chart(title, [], xdata, ydata, series, xname, yname, all_labels=True)
    c["visualMap"] = {
        "min": 0,
        "max": max(item[2] for item in seriesdata) if len(seriesdata) else 0,
        "orient": "vertical",
        "right": 0,
        "top": "center",
    }
    return c


def rows_to_xy(rows: list[tuple[str, int]]) -> tuple[list[str], DataT]:
    """
    Convert rows as returned by sqlite .fetchall() for query:
        SELECT column, COUNT(*) GROUP BY column
    Returns: axisdata, seriesdata for bar() function
    """
    return [row[0] for row in rows], [row[1] for row in rows]


def rows_to_xy_multi(
    rows: list[tuple[str, str, int]],
    case_sensitive: bool = True,
    restore_case: bool = False,
    a_limit: int | None = None,
) -> tuple[list[str], MultiDataT]:
    """
    Convert rows as returned by sqlite .fetchall() for query:
        SELECT column_a, column_b, COUNT(*) GROUP BY column_a, column_b
    Input:
    [a1, b1, c1]
    [a1, b2, c2]
    [a2, b1, c3]
    Returns:
    Tuple of axisdata: [a1, a2] and seriesdata: {b1: [c1, c3], b2: [c2, 0]
    Where a appears on the x axis, b appears in the legend (is stacked), and c is data.
    For bar() function.
    """
    if restore_case:
        assert not case_sensitive, "restore_case makes no sense if case sensitive"

    # Create list of a values, sorted by total b for every a
    a_list: list[str] = []
    a_counts: dict[str, int] = {}  # for sorting
    for a, _b, c in rows:
        if not case_sensitive:
            a = a.lower()

        if a not in a_list:
            a_list.append(a)
            a_counts[a] = 0

        a_counts[a if case_sensitive else a.lower()] += c

    axisdata = sorted(a_list, key=lambda a: -a_counts[a])

    if a_limit is not None and len(axisdata) > a_limit:
        axisdata = axisdata[:a_limit]

    seriesdata: MultiDataT = {}

    for a, b, c in rows:
        try:
            a_index = axisdata.index(a if case_sensitive else a.lower())
        except ValueError:
            continue  # outside of limit
        if b not in seriesdata:
            seriesdata[b] = [0] * len(axisdata)
        seriesdata[b][a_index] = c

    if restore_case:
        # Restore original case
        for i, a in enumerate(axisdata):
            for a2, _b, _c in rows:
                if a.lower() == a2.lower():
                    axisdata[i] = a2
                    break

    return axisdata, seriesdata


def chart_last_chosen(conn: Connection, _period: StatsPeriod) -> Chart | None:
    """
    Last chosen chart
    """
    cur = conn.cursor()
    result_playlists = [row[0] for row in cur.execute("SELECT playlist FROM track GROUP BY playlist ORDER BY playlist")]
    result_week = cur.execute(
        "SELECT playlist, COUNT(last_chosen) FROM track WHERE unixepoch() - last_chosen <= 60*60*24*7 GROUP BY playlist ORDER BY playlist"
    ).fetchall()
    result_month = cur.execute(
        "SELECT playlist, COUNT(last_chosen) FROM track WHERE unixepoch() - last_chosen <= 60*60*24*30 AND unixepoch() - last_chosen > 60*60*24*7 GROUP BY playlist ORDER BY playlist"
    ).fetchall()
    result_year = cur.execute(
        "SELECT playlist, COUNT(last_chosen) FROM track WHERE unixepoch() - last_chosen <= 60*60*24*365 AND unixepoch() - last_chosen > 60*60*24*30 GROUP BY playlist ORDER BY playlist"
    ).fetchall()
    result_long_ago = cur.execute(
        "SELECT playlist, COUNT(last_chosen) FROM track WHERE unixepoch() - last_chosen > 60*60*24*365 AND last_chosen != 0 GROUP BY playlist ORDER BY playlist"
    ).fetchall()
    result_never = cur.execute(
        "SELECT playlist, COUNT(last_chosen) FROM track WHERE last_chosen == 0 GROUP BY playlist ORDER BY playlist"
    ).fetchall()

    axis = [_("Past 7 days"), _("Past 30 days"), _("Past 365 days"), _("Long ago"), _("Never")]
    series: MultiDataT = {}

    for playlist in result_playlists:
        series[playlist] = [0] * 6

    for i, result in enumerate((result_week, result_month, result_year, result_long_ago, result_never)):
        for playlist, count in result:
            series[playlist][i] = count

    return multibar(_("When tracks were last chosen by algorithm"), axis, series, _("time ago"), _("track count"))


def chart_playlist_track_count(conn: Connection, _period: StatsPeriod) -> Chart:
    counts = conn.execute("SELECT playlist, COUNT(*) FROM track GROUP BY playlist ORDER BY COUNT(*) DESC").fetchall()
    return bar(_("Number of tracks in playlists"), *rows_to_xy(counts), _("playlist"), _("track count"))


def chart_playlist_track_mean_duration(conn: Connection, _period: StatsPeriod) -> Chart:
    means = conn.execute(
        "SELECT playlist, AVG(duration)/60 FROM track GROUP BY playlist ORDER BY AVG(duration) DESC"
    ).fetchall()
    return bar(
        _("Mean duration of tracks in playlists"),
        *rows_to_xy(means),
        _("playlist"),
        _("duration (minutes)"),
    )


def chart_playlist_total_duration(conn: Connection, _period: StatsPeriod) -> Chart:
    totals = conn.execute(
        "SELECT playlist, SUM(duration)/60 FROM track GROUP BY playlist ORDER BY SUM(duration) DESC"
    ).fetchall()
    return bar(
        _("Total duration of tracks in playlists"),
        *rows_to_xy(totals),
        _("playlist"),
        _("duration (minutes)"),
    )


def chart_track_year(conn: Connection, _period: StatsPeriod) -> Chart | None:
    """
    Track release year chart
    """
    min_year, max_year = conn.execute("SELECT MAX(1950, MIN(year)), MIN(2030, MAX(year)) FROM track").fetchone()
    if min_year is None or max_year is None:
        return None

    data: dict[str, list[int]] = {}

    if min_year and max_year:
        for (playlist,) in conn.execute(
            "SELECT playlist FROM track GROUP BY playlist ORDER BY COUNT(*) DESC LIMIT 15"
        ).fetchall():
            data[playlist] = [0] * (max_year - min_year + 1)

        rows = conn.execute(
            """
            SELECT playlist, year, COUNT(year)
            FROM track
            WHERE year IS NOT NULL
            GROUP BY playlist, year
            ORDER BY year ASC
            """
        ).fetchall()
        for playlist, year, count in rows:
            if year < min_year or year > max_year or playlist not in data:
                continue
            data[playlist][year - min_year] = count

    return multibar(
        _("Track release year distribution"),
        [str(year) for year in range(min_year, max_year + 1)],
        data,
        _("year"),
        _("track count"),
    )


def chart_users(conn: Connection, period: StatsPeriod) -> Chart | None:
    rows = conn.execute(
        f"""
        SELECT COALESCE(nickname, username), playlist, COUNT(*)
        FROM history JOIN user ON history.user = user.id
        WHERE {period.query_where}
        GROUP BY user, playlist
        """
    ).fetchall()
    return multibar(_("Active users"), *rows_to_xy_multi(rows, a_limit=15), _("user"), _("play count"), all_labels=True)


def chart_playlists(conn: Connection, period: StatsPeriod) -> Chart | None:
    # the same as chart_users but with two columns swapped
    rows = conn.execute(
        f"""
        SELECT playlist, COALESCE(nickname, username), COUNT(*)
        FROM history JOIN user ON history.user = user.id
        WHERE {period.query_where}
        GROUP BY user, playlist
        """
    ).fetchall()
    return multibar(
        _("Played playlists"), *rows_to_xy_multi(rows, a_limit=15), _("playlist"), _("play count"), all_labels=True
    )


def chart_tracks(conn: Connection, period: StatsPeriod) -> Chart | None:
    rows = conn.execute(
        f"""
        SELECT track, COALESCE(nickname, username), COUNT(*)
        FROM history
            JOIN user ON history.user = user.id
        WHERE {period.query_where}
            AND track IN (SELECT track
                            FROM history
                            WHERE {period.query_where}
                            GROUP BY track
                            ORDER BY COUNT(*) DESC
                            LIMIT 10)
        GROUP BY track, user
        """
    ).fetchall()
    return multibar(_("Most played tracks"), *rows_to_xy_multi(rows), _("play count"), _("track"), horizontal=True)


def chart_artists(conn: Connection, period: StatsPeriod) -> Chart | None:
    rows = conn.execute(
        f"""
        SELECT artist, COALESCE(nickname, username), COUNT(*)
        FROM history
            INNER JOIN track ON history.track = track.path
            JOIN track_artist ON track_artist.track = track.path
            JOIN user ON history.user = user.id
        WHERE {period.query_where}
            AND artist IN (SELECT artist
                            FROM history
                                INNER JOIN track ON history.track = track.path
                                JOIN track_artist ON track_artist.track = track.path
                            WHERE {period.query_where}
                            GROUP BY artist
                            ORDER BY COUNT(*) DESC
                            LIMIT 10)
        GROUP BY artist, user
        """
    ).fetchall()
    return multibar(
        _("Most played artists"),
        *rows_to_xy_multi(rows, case_sensitive=False, restore_case=True),
        _("play count"),
        _("artist"),
        horizontal=True,
    )


def chart_albums(conn: Connection, period: StatsPeriod) -> Chart | None:
    rows = conn.execute(
        f"""
        SELECT album, COALESCE(nickname, username), COUNT(*)
        FROM history
            INNER JOIN track ON history.track = track.path
            JOIN user ON history.user = user.id
        WHERE {period.query_where}
            AND album IN (SELECT album
                            FROM history
                                INNER JOIN track ON history.track = track.path
                            WHERE {period.query_where}
                            GROUP BY album
                            ORDER BY COUNT(*) DESC
                            LIMIT 10)
        GROUP BY album, user
        """
    ).fetchall()
    return multibar(
        _("Most played albums"),
        *rows_to_xy_multi(rows, case_sensitive=False, restore_case=True),
        _("play count"),
        _("album"),
        horizontal=True,
    )


def chart_time_of_day(conn: Connection, period: StatsPeriod) -> Chart | None:
    time_of_day: MultiDataT = {}

    for hour, username, count in conn.execute(
        f"""
        SELECT strftime('%H', timestamp, 'unixepoch', 'localtime') AS hour, COALESCE(nickname, username), COUNT(*)
        FROM history JOIN user ON history.user = user.id
        WHERE {period.query_where}
        GROUP BY hour, user
        """
    ):
        if username not in time_of_day:
            time_of_day[username] = [0] * 24
        time_of_day[username][int(hour)] += count
    return multibar(
        _("Time of day"), [f"{i:02}:00" for i in range(0, 24)], time_of_day, _("hour of day"), _("play count")
    )


def chart_day_of_week(conn: Connection, period: StatsPeriod) -> Chart | None:
    series: MultiDataT = {}

    for day, username, count in conn.execute(
        f"""
        SELECT strftime('%w', timestamp, 'unixepoch', 'localtime') AS day, COALESCE(nickname, username), COUNT(*)
        FROM history JOIN user ON history.user = user.id
        WHERE {period.query_where}
        GROUP BY day, user
        """
    ):
        if username not in series:
            series[username] = [0] * 7
        series[username][int(day)] += count
    return multibar(
        _("Day of week"),
        [_("Sunday"), _("Monday"), _("Tuesday"), _("Wednesday"), _("Thursday"), _("Friday"), _("Saturday")],
        series,
        _("day of week"),
        _("play count"),
    )


def chart_week_of_year(conn: Connection, period: StatsPeriod) -> Chart | None:
    if period.end - period.start < 300 * 24 * 60 * 60:
        return None

    series: MultiDataT = {}

    for week, username, count in conn.execute(
        f"""
        SELECT strftime('%W', timestamp, 'unixepoch', 'localtime') AS week, COALESCE(nickname, username), COUNT(*)
        FROM history JOIN user ON history.user = user.id
        WHERE {period.query_where}
        GROUP BY week, user
        """,
    ):
        if username not in series:
            series[username] = [0] * 52

        week = int(week)
        if week == 0:  # last week of previous year
            week = 51
        elif week == 53:  # first week of next year
            week = 0
        else:
            week = week - 1
        series[username][week] += count

    axis = [f"{i:02}" for i in range(1, 53)]
    return multibar(_("Plays by week"), axis, series, _("week number"), _("play count"))


def chart_unique_artists(conn: Connection, _period: StatsPeriod) -> Chart | None:
    rows = conn.execute(
        """
        SELECT playlist, ROUND(COUNT(DISTINCT artist) / CAST(COUNT(artist) AS float), 2) AS ratio
        FROM track INNER JOIN track_artist ON track.path = track_artist.track
        GROUP BY playlist
        ORDER BY ratio
        """
    ).fetchall()
    return bar(_("Artist diversity"), *rows_to_xy(rows), _("playlist"), _("distinct artist ratio"))


def chart_popular_artists(conn: Connection, _period: StatsPeriod) -> Chart | None:
    # TODO try COUNT(*)
    rows = conn.execute(
        f"""
        SELECT artist, playlist, COUNT(artist)
        FROM track INNER JOIN track_artist ON track.path = track_artist.track
        WHERE artist IN (SELECT artist FROM track_artist GROUP BY artist ORDER BY COUNT(artist) DESC LIMIT 15)
        GROUP BY artist, playlist
        """
    ).fetchall()
    return multibar(
        _("Artists in playlists"),
        *rows_to_xy_multi(rows, case_sensitive=False, restore_case=True),
        _("count"),
        "artist",
        horizontal=True,
    )


def chart_popular_tags(conn: Connection, _period: StatsPeriod) -> Chart | None:
    rows = conn.execute(
        f"""
        SELECT tag, playlist, COUNT(tag)
        FROM track INNER JOIN track_tag ON track.path = track_tag.track
        WHERE tag IN (SELECT tag FROM track_tag GROUP BY tag ORDER BY COUNT(tag) DESC LIMIT 15)
        GROUP BY tag, playlist
        """
    ).fetchall()
    return multibar(
        _("Tags in playlists"),
        *rows_to_xy_multi(rows, case_sensitive=False, restore_case=False),
        _("count"),
        _("tag"),
        horizontal=True,
    )


def _chart_artist_similarity(conn: Connection) -> tuple[LegendDataT, HeatmapDataT]:
    result = conn.execute(
        """
        SELECT t1.playlist, t2.playlist, COUNT(DISTINCT ta1.artist)
        FROM track_artist ta1
            JOIN track t1 ON ta1.track = t1.path
            JOIN track_artist ta2 ON ta1.artist = ta2.artist
            JOIN track t2 ON ta2.track = t2.path
        GROUP BY t1.playlist, t2.playlist
        """
    )

    matching_artist_counts: dict[tuple[str, str], int] = {}
    for playlist1, playlist2, count in result:
        matching_artist_counts[(playlist1, playlist2)] = count

    rows = conn.execute(
        """
        SELECT track.playlist, COUNT(DISTINCT artist)
        FROM track_artist JOIN track ON track_artist.track = track.path
        GROUP BY track.playlist
        ORDER BY COUNT(DISTINCT track) DESC
        LIMIT 15
        """
    ).fetchall()
    playlists: list[str] = [row[0] for row in rows]
    artist_counts: list[int] = [row[1] for row in rows]

    series: list[tuple[int, int, float]] = []
    for i1, p1 in enumerate(playlists):
        for i2, p2 in enumerate(playlists):
            if i1 == i2:
                continue
            elif (p1, p2) in matching_artist_counts:
                percentage = (matching_artist_counts[(p1, p2)] / (artist_counts[i1] + artist_counts[i2])) * 100
                series.append((i1, i2, round(percentage, 2)))
            else:
                series.append((i1, i2, 0))

    return playlists, series


def chart_artist_similarity(conn: Connection, _period: StatsPeriod) -> Chart | None:
    # Chart is quite slow and I'm not sure how to speed it up. Cache it to improve loading speed when switching
    # between periods.
    data = cast(tuple[LegendDataT, HeatmapDataT] | None, cache.memory_get("artist similarity"))
    if data is None:
        data = _chart_artist_similarity(conn)
        cache.memory_store("artist similarity", data, cache.HOUR)
    playlists, series = data
    return heatmap(
        _("Artist similarity"),
        _("Percentage of artists in common"),
        playlists,
        playlists,
        series,
        _("playlist"),
        _("playlist"),
    )


CHARTS: list[Callable[[Connection, StatsPeriod], Chart | None]] = [
    chart_users,
    chart_playlists,
    chart_time_of_day,
    chart_day_of_week,
    chart_week_of_year,
    chart_tracks,
    chart_albums,
    chart_artists,
    chart_artist_similarity,
    chart_popular_artists,
    chart_popular_tags,
    chart_track_year,
    chart_last_chosen,
    chart_playlist_track_count,
    chart_playlist_total_duration,
    chart_playlist_track_mean_duration,
    chart_unique_artists,
]


async def get_chart(chart_id: int, period: StatsPeriod):
    _LOGGER.debug("generating chart %s for period %s", chart_id, period)

    def generate_chart():
        with db.MUSIC.connect() as conn:
            return CHARTS[chart_id](conn, period)

    return await asyncio.to_thread(generate_chart)
