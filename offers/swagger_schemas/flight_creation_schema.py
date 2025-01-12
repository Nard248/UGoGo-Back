from drf_yasg import openapi

flight_creation_data_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "from_airport_id": openapi.Schema(
            default=1,
            type=openapi.TYPE_INTEGER,
            description="ID of the departure airport."
        ),
        "to_airport_id": openapi.Schema(
            default=2,
            type=openapi.TYPE_INTEGER,
            description="ID of the arrival airport."
        ),
        "departure_datetime": openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATETIME,
            description="ISO 8601 formatted departure date and time."
        ),
        "arrival_datetime": openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATETIME,
            description="ISO 8601 formatted arrival date and time."
        )
    },
    required=["publisher", "from_airport_id", "to_airport_id", "departure_datetime", "arrival_datetime"]
)
