from email.policy import default

from drf_yasg import openapi

item_creation_body_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "name": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Name of the item."
        ),
        "weight": openapi.Schema(
            type=openapi.TYPE_NUMBER,
            format=openapi.FORMAT_DECIMAL,
            description="Weight of the item (in kg).",
            default=10
        ),
        "dimensions": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Dimensions of the item (e.g., LxWxH).",
            default="10X10"
        ),
        "fragile": openapi.Schema(
            type=openapi.TYPE_BOOLEAN,
            description="Indicates whether the item is fragile.",
            default=False,
        ),
        "description": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Description of the item."
        ),
        "pickup_name": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="First name of the pickup person."
        ),
        "pickup_surname": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Surname of the pickup person."
        ),
        "pickup_phone": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Phone number of the pickup person."
        ),
        "pickup_email": openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_EMAIL,
            description="Email address of the pickup person."
        ),
        "category_ids": openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Items(type=openapi.TYPE_INTEGER),
            description="List of category IDs associated with the item."
        ),
        "pictures": openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Items(
                type=openapi.TYPE_OBJECT,
                properties={
                    "image_path": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Path to the image of the item."
                    )
                }
            ),
            description="List of pictures associated with the item."
        ),
        "state": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Current state of the item (e.g., 'draft')."
        )
    },
    required=["name", "weight", "dimensions", "fragile", "description", "pickup_name", "pickup_surname", "pickup_phone",
              "pickup_email", "category_ids", "pictures", "state"]
)
