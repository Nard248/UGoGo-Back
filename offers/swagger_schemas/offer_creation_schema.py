from drf_yasg import openapi

from offers.swagger_schemas.flight_creation_schema import flight_creation_data_schema

offer_creation_body_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "flight_data": flight_creation_data_schema,
        "courier_id": openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description="ID of the courier handling the flight."
        ),
        "status": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Optional status of the courier (e.g., 'available').",
            enum=["available", "unavailable"],
            nullable=True
        ),
        "item_category_id": openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description="ID of the item category being transported.",
            nullable=True
        ),
        "fragile": openapi.Schema(
            type=openapi.TYPE_BOOLEAN,
            description="Indicates whether the item is fragile.",
            nullable=True
        ),
        "notes": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Optional additional notes.",
            nullable=True
        ),
        "price": openapi.Schema(
            default=10,
            type=openapi.TYPE_NUMBER,
            format=openapi.FORMAT_DECIMAL,
            description="The price for transporting the items."
        ),
        "available_weight": openapi.Schema(
            default=10,
            type=openapi.TYPE_NUMBER,
            format=openapi.FORMAT_DECIMAL,
            description="Available weight capacity for the courier (in kg)."
        ),
        "available_space": openapi.Schema(
            default=10,
            type=openapi.TYPE_NUMBER,
            format=openapi.FORMAT_DECIMAL,
            description="Available space capacity for the courier (in cubic meters)."
        ),
    },
    required=["flight_data", "courier_id", "price", "available_weight", "available_space"]
)
