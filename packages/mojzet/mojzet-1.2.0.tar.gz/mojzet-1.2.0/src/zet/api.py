import json
from dataclasses import dataclass

from aiohttp import ClientResponse, ClientSession
from multidict import CIMultiDictProxy

from zet.entities import IncomingTrip, News, Route, Stop, Trip, TripStop, Vehicle


@dataclass(frozen=True)
class Response[T]:
    body: str
    status: int
    headers: CIMultiDictProxy[str]

    def json(self) -> T:
        return json.loads(self.body)

    @classmethod
    async def from_client_response(cls, response: ClientResponse):
        return cls(
            body=await response.text(),
            status=response.status,
            headers=response.headers,
        )


async def get_newsfeed(session: ClientSession) -> Response[list[News]]:
    async with session.get("/NewsProxyService.Api/api/newsfeed") as response:
        response.raise_for_status()
        return await Response.from_client_response(response)


async def get_routes(session: ClientSession) -> Response[list[Route]]:
    async with session.get("/TimetableService.Api/api/gtfs/routes") as response:
        response.raise_for_status()
        return await Response.from_client_response(response)


async def get_stops(session: ClientSession) -> Response[list[Stop]]:
    async with session.get("/TimetableService.Api/api/gtfs/stops") as response:
        response.raise_for_status()
        return await Response.from_client_response(response)


async def get_route_trips(session: ClientSession, route_id: str) -> Response[list[Trip]]:
    params = {"routeId": route_id, "daysFromToday": "0"}
    async with session.get("/TimetableService.Api/api/gtfs/routeTrips", params=params) as response:
        response.raise_for_status()
        return await Response.from_client_response(response)


async def get_vehicles(session: ClientSession) -> Response[list[Vehicle]]:
    async with session.get("/TransportService.Api/api/Vehicle") as response:
        response.raise_for_status()
        return await Response.from_client_response(response)


async def get_incoming_trips(session: ClientSession, stop_id: str) -> Response[list[IncomingTrip]]:
    path = "/TimetableService.Api/api/gtfs/stopIncomingTrips"
    params = {"stopId": stop_id, "isMapView": "false"}
    async with session.get(path, params=params) as response:
        return await Response.from_client_response(response)


async def get_trip_stop_times(session: ClientSession, trip_id: str) -> Response[list[TripStop]]:
    path = "/TimetableService.Api/api/gtfs/tripStopTimes"
    params = {"tripId": trip_id, "daysFromToday": 0}
    async with session.get(path, params=params) as response:
        return await Response.from_client_response(response)
