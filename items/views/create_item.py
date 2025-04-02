from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from items.swagger_schemas.unified_item_schema import item_creation_body_schema
from items.serializers import ItemSerializer


class UnifiedItemCreateView(generics.GenericAPIView):
    """
    Single endpoint to create Item, pictures, categories, pickup info, etc.
    """
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create an item, pictures, categories, etc. in a single request.",
        request_body=item_creation_body_schema,
        responses={
            201: "Created the Item successfully.",
            400: "Invalid data",
            401: "Unauthorized"
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            item = serializer.save()
            return Response(
                {
                    "message": "Item created successfully!",
                    "item_id": item.id
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
