import logging
import textwrap

from aiohttp import ClientSession
import click

from zet import api, __version__
from zet.app import ZetApp
from zet.decorators import async_command, pass_session
from zet.entities import Stop
from zet.output import format_direction, format_route_type, format_time, format_tracked, table_dump


json_option = click.option(
    "--json",
    is_flag=True,
    help="Dump data as raw JSON instead of a human readable format.",
)


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.version_option(__version__)
def zet(debug: bool):
    if debug:
        logging.basicConfig(level=logging.DEBUG)


@zet.command()
@json_option
@async_command
@pass_session
async def news(session, json: bool):
    """Show news feed"""
    response = await api.get_newsfeed(session)

    if json:
        click.echo(response.body)
        return

    news = response.json()

    def _generator():
        first = True
        for item in news:
            if not first:
                yield click.style("-" * 80, dim=True) + "\n\n"
            yield click.style(item["title"], bold=True) + "\n\n"
            for line in textwrap.wrap(item["description"], 80):
                yield line + "\n"
            yield "\n"
            yield click.style(item["link"], underline=True, dim=True) + "\n"
            yield click.style(item["datePublished"], dim=True) + "\n\n"
            first = False

    click.echo_via_pager(_generator())


@zet.command()
@async_command
@pass_session
async def tui(session):
    app = ZetApp(session)
    await app.run_async()


@zet.command()
@click.option("-p", "--pager/--no-pager")
@json_option
@async_command
@pass_session
async def routes(session, pager: bool, json: bool):
    """List routes"""
    response = await api.get_routes(session)

    if json:
        click.echo(response.body)
        return

    routes = response.json()

    table_dump(
        routes,
        {
            "Type": lambda r: format_route_type(r["routeType"]),
            "No": lambda r: str(r["id"]),
            "From": lambda r: r["departureHeadsign"],
            "To": lambda r: r["destinationHeadsign"],
        },
        pager=pager,
    )


@zet.command()
@click.option("-p", "--pager/--no-pager")
@click.option("-n", "--name", help="Station name")
@json_option
@async_command
@pass_session
async def stops(session, pager: bool, name: str | None, json: bool):
    """List stops"""
    response = await api.get_stops(session)

    if json:
        click.echo(response.body)
        return

    stops = response.json()

    if name:
        stops = [s for s in stops if name in s["normalizedSearchName"]]

    table_dump(
        stops,
        {
            "ID": lambda s: str(s["id"]),
            "Name": lambda s: s["name"],
            "Latitude": lambda s: str(s["stopLat"]),
            "Longitude": lambda s: str(s["stopLong"]),
            "Type": lambda s: format_route_type(s["routeType"]),
            "Trips": lambda s: _trips(s),
        },
        pager=pager,
    )


def _trips(stop: Stop):
    return ", ".join(trip["routeCode"] for trip in stop["trips"])


@zet.command()
@click.argument("stop_id")
@click.option("-p", "--pager/--no-pager")
@click.option("-r", "--route", "route_id")
@json_option
@async_command
@pass_session
async def trips(session, stop_id: str, pager: bool, route_id: str, json: bool):
    """List arrivals for a given stop"""
    response = await api.get_incoming_trips(session, stop_id)

    if json:
        click.echo(response.body)
        return

    trips = response.json()

    if route_id:
        trips = [t for t in trips if t["routeShortName"] == route_id]

    table_dump(
        trips,
        {
            "#": lambda t: t["routeShortName"],
            "Destination": lambda t: t["headsign"],
            "Arrival": lambda t: format_time(t["expectedArrivalDateTime"]),
            "Tracked?": lambda t: format_tracked(t["hasLiveTracking"]),
        },
        pager=pager,
    )


@zet.command()
@click.argument("trip_id")
@click.option("-p", "--pager/--no-pager")
@json_option
@async_command
@pass_session
async def trip_stops(session, trip_id: str, pager: bool, json: bool):
    """List stops for a given trip"""
    response = await api.get_trip_stop_times(session, trip_id)

    if json:
        click.echo(response.body)
        return

    trips = response.json()

    table_dump(
        trips,
        {
            "#": lambda t: str(t["id"]),
            "Stop": lambda t: t["stopName"],
            "Arrival": lambda t: format_time(t["expectedArrivalDateTime"]),
            "Arrived?": lambda t: str(t["isArrived"]),
            "Predict?": lambda t: str(t["isArrivedPrediction"]),
        },
        pager=pager,
    )


@zet.command()
@click.argument("route_id")
@click.option("-p", "--pager/--no-pager")
@click.option(
    "-d",
    "--direction",
    type=click.Choice(["A", "B"], case_sensitive=False),
    help="Show only trips in the given direction",
)
@json_option
@async_command
@pass_session
async def route_trips(session, route_id: str, pager: bool, direction: str | None, json: bool):
    """List trips for a given route"""
    response = await api.get_route_trips(session, route_id)

    if json:
        click.echo(response.body)
        return

    trips = response.json()

    if direction == "A":
        trips = [t for t in trips if t["direction"] == 0]

    if direction == "B":
        trips = [t for t in trips if t["direction"] == 1]

    table_dump(
        trips,
        {
            "Trip ID": lambda t: str(t["id"]),
            "Direction": lambda t: format_direction(t["direction"]),
            "Headsign": lambda t: t["headsign"],
            "Depart": lambda t: format_time(t["departureDateTime"]),
            "Arrive": lambda t: format_time(t["arrivalDateTime"]),
            "Tracked?": lambda t: str(t["hasLiveTracking"]),
        },
        pager=pager,
    )


@zet.command()
@click.option("-p", "--pager/--no-pager")
@json_option
@async_command
@pass_session
async def vehicles(session: ClientSession, pager: bool, json: bool):
    """List vehicles"""
    response = await api.get_vehicles(session)

    if json:
        click.echo(response.body)
        return

    vehicles = response.json()

    table_dump(
        vehicles,
        {
            "#": lambda x: str(x["id"]),
            "Garage#": lambda x: x["garageNumber"],
            "Plate": lambda x: x["numberPlate"] or "",
            "Description": lambda x: x["description"],
        },
        pager=pager,
    )
