from drf_yasg import openapi

login_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "email": openapi.Schema(
            default="glastyan.simon12@gmail.com",
            type=openapi.TYPE_STRING,
            description="The entity publishing the flight, e.g., airline."
        ),
        "password": openapi.Schema(
            default="112233",
            type=openapi.TYPE_STRING,
            description="ID of the departure airport."
        )
    },
    required=["email", "password"]
)
