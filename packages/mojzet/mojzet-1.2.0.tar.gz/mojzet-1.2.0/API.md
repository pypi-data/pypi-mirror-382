# ZET API

## Public routes

* GET https://api.zet.hr/AuthService.Api/api/MobileApplication/CheckLastMobileApplicationVersion
* GET https://api.zet.hr/NewsProxyService.Api/api/newsfeed
* GET https://api.zet.hr/TimetableService.Api/api/gtfs/routes
* GET https://api.zet.hr/TimetableService.Api/api/gtfs/shapes
* GET https://api.zet.hr/TimetableService.Api/api/gtfs/stopIncomingTrips?stopId=188_2&isMapView=false
* GET https://api.zet.hr/TimetableService.Api/api/gtfs/stops
* GET https://api.zet.hr/TimetableService.Api/api/gtfs/tripStopTimes?tripId=0_21_207_2_10638&daysFromToday=0
* GET https://api.zet.hr/TransportService.Api/api/Station?projectNumber=&stopId=&stopCode=&stopName=&trafficAreaIds=&trafficZoneIds=&status=1

## Authenticated routes

* GET https://api.zet.hr/AccountService.Api/api/Favorite/favorites
* GET https://api.zet.hr/AccountService.Api/api/account
* GET https://api.zet.hr/AccountService.Api/api/account/barcode
* GET https://api.zet.hr/AccountService.Api/api/message
* GET https://api.zet.hr/OrderService.Api/api/v1/open/orders/order?completedOnly=true&PageSize=10&PageNumber=1
* GET https://api.zet.hr/TicketService.Api/api/v1/open/tickets/ticket/filteredTickets?isControlTicket=false&validOnly=false&includeValidations=true
* GET https://api.zet.hr/TicketService.Api/api/v1/open/tickets/ticket/paginatedTickets?PageSize=10&PageNumber=2

## Register

```
POST https://api.zet.hr/AuthService.Api/api/account/register

{
  "email": "user@example.com",
  "password": "pass",
  "confirmPassword": "pass"
}
```


## Login

```
POST https://api.zet.hr/AuthService.Api/api/auth/login

{
  "username": "user@example.com",
  "password": "password",
  "revokeOtherTokens": false,
  "fcmToken": "..."
}
```

Response:

```
{
  "accessToken": "...",
  "refreshToken": "..."
}
```


## Refresh tokens

```
POST https://api.zet.hr/AuthService.Api/api/auth/refreshTokens

{
  "refreshToken": "..."
}
```

Reponse:

```
{
  "accessToken": "...",
  "refreshToken": "..."
}
```
