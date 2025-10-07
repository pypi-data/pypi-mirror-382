from __future__ import annotations

from enum import IntEnum
from typing import TypedDict

type RouteId = int
type ShapeId = str
type StopId = int
type TripId = int
type VehicleId = int
type Direction = int


# GTFS Route Type
# https://gtfs.org/documentation/schedule/reference/#routestxt
class RouteType(IntEnum):
    TRAM = 0
    SUBWAY = 1
    RAIL = 2
    BUS = 3
    FERRY = 4
    CABLE = 5
    AERIAL = 6
    FUNICULAR = 7
    TROLLEYBUS = 11
    MONORAIL = 12


class News(TypedDict):
    title: str
    description: str
    link: str
    datePublished: str
    type: RouteType
    lines: list[int]
    stations: list[int]
    validFrom: str
    validTo: str


class Route(TypedDict):
    id: RouteId
    shortName: str
    longName: str
    routeType: RouteType
    departureHeadsign: str
    destinationHeadsign: str
    normalizedSearchName: str


class Stop(TypedDict):
    id: StopId
    name: str
    routeType: RouteType
    trips: list[StopTrip]
    stopLat: float
    stopLong: float
    parentStopId: StopId
    normalizedSearchName: str


class StopTrip(TypedDict):
    routeCode: str
    tripHeadsigns: list[str]


class Trip(TypedDict):
    id: TripId
    direction: Direction
    headsign: str
    departureDateTime: str
    arrivalDateTime: str
    hasLiveTracking: bool
    tripStatus: int  # ???
    vehicles: list[TripVehicle]
    shapeId: ShapeId


class TripVehicle(TypedDict):
    id: str
    position: Position


class TripStop(TypedDict):
    id: StopId
    stopName: str
    stopSequence: int
    expectedArrivalDateTime: str
    isArrived: bool
    isArrivedPrediction: bool
    stopLat: float
    stopLong: float
    trip: Trip


class Position(TypedDict):
    latitude: float
    longitude: float


class IncomingTrip(TypedDict):
    tripId: str
    routeShortName: str
    headsign: str
    expectedArrivalDateTime: str
    hasLiveTracking: bool
    daysFromToday: int


class Vehicle(TypedDict):
    id: VehicleId
    active: bool
    dateCreated: str
    garageNumber: str
    numberPlate: str | None
    vehicleTypeID: int
    isForDisabledPeople: bool
    isAutomaticImport: bool
    description: str
    factoryNumber: str
