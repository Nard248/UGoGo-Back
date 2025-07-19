# Advanced Offer Search API

`GET /offers/offers/advanced_search/`

This endpoint allows senders to search available shipping offers using multiple criteria. All parameters are optional and combined using **AND** logic.

## Query Parameters
- `origin_airport` – IATA airport code of departure.
- `destination_airport` – IATA airport code of arrival.
- `min_price`/`max_price` – price range.
- `departure_after`/`departure_before` – filter by flight departure datetime range.
- `arrival_after`/`arrival_before` – filter by flight arrival datetime range.
- `categories` – list of item category IDs the courier must accept.
- `weight` – required item weight in kilograms.
- `space` – required item space in cubic meters.

Only offers with status `available` and couriers with verified passports are returned. Results include remaining capacity and related flight information. Offers are ordered by price and departure time.

## Example Request
```bash
curl -G \
  -d origin_airport=JFK \
  -d destination_airport=LAX \
  -d min_price=10 \
  -d max_price=200 \
  -d departure_after="2024-06-01T00:00" \
  -d categories=1 \
  http://<host>/offers/offers/advanced_search/
```

## Example Response
```json
[
  {
    "id": 5,
    "user_flight": {
      "flight": {
        "from_airport": {"airport_code": "JFK"},
        "to_airport": {"airport_code": "LAX"},
        "departure_datetime": "2024-06-02T10:00:00Z",
        "arrival_datetime": "2024-06-02T18:00:00Z"
      },
      "user": {"id": 2, "email": "courier@example.com"}
    },
    "status": "available",
    "price": "120.00",
    "available_weight": "20.00",
    "available_space": "2.00"
  }
]
```
