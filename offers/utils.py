from offers.views.flight_views import FlightListCreateAPIView


def create_flight(flight_data):
    flight_view = FlightListCreateAPIView.as_view()
    flight_request = request._request
    flight_request.data = flight_data

    flight_response = flight_view(flight_request)

    if flight_response.status_code != 201:
        return Response(
            {"error": "Failed to create flight.", "details": flight_response.data},
            status=flight_response.status_code,
        )

    flight_id = flight_response.data.get("id")
    return flight_id
