from typing import Callable, Iterable, List

import click
from dateutil.parser import parse

from zet.entities import Direction, RouteType

type TableSpec[T] = dict[str, Callable[[T], str]]


def table_dump[T](items: Iterable[T], spec: TableSpec[T], *, pager: bool = False):
    headers = list(spec.keys())
    rows = [[lmbda(item) for lmbda in spec.values()] for item in items]
    if pager:
        click.echo_via_pager(generate_table(headers, rows))
    else:
        click.echo("".join(generate_table(headers, rows)))


def generate_table(headers: list[str], data: list[List[str]]):
    widths = [[len(str(cell)) for cell in row] for row in data + [headers]]
    widths = [max(width) for width in zip(*widths)]

    def get_line(row):
        line = ""
        for idx, cell in enumerate(row):
            width = widths[idx]
            line += str(cell).ljust(width)
            line += "  "
        return line + "\n"

    underlines = ["-" * width for width in widths]

    yield get_line(headers)
    yield get_line(underlines)

    for row in data:
        yield get_line(row)


def format_direction(direction: Direction) -> str:
    if direction == 0:
        return "A"
    if direction == 1:
        return "B"
    return str(direction)


def format_time(value: str) -> str:
    return parse(value).time().strftime("%H:%M")


def format_relative_time(value: str) -> str:
    return parse(value).time().strftime("%H:%M")


def format_tracked(value: bool) -> str:
    return click.style("Tracked", fg="green") if value else click.style("Nope", fg="red")


def format_route_type(type: RouteType) -> str:
    match type:
        case RouteType.TRAM:
            return "Tram"
        case RouteType.SUBWAY:
            return "Subway"
        case RouteType.RAIL:
            return "Rail"
        case RouteType.BUS:
            return "Bus"
        case RouteType.FERRY:
            return "Ferry"
        case RouteType.CABLE:
            return "Cable"
        case RouteType.AERIAL:
            return "Aerial"
        case RouteType.FUNICULAR:
            return "Funicular"
        case RouteType.TROLLEYBUS:
            return "Trolleybus"
        case RouteType.MONORAIL:
            return "Monorail"
        case _:
            return f"Unknown ({type})"
