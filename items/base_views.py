from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView

from items.models.items import Item, ItemCategory
from flight_requests.models.request import Request
from items.serializers import (
    ItemSerializer,
    RequestSerializer
)
from items.permissions import IsOwnerOrReadOnly, IsCourierOfOffer

from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ItemListCreateAPIView(generics.ListCreateAPIView):
    """
    GET: List user's own items
    POST: Create a new item (owned by the request.user)
    """
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Item.objects.filter(user=self.request.user).prefetch_related('categories', 'pictures')

    @swagger_auto_schema(operation_description="List all items belonging to the current user.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Create a new item for the current user.")
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ItemDestroyAPIView(generics.DestroyAPIView):
    """
    DELETE: Remove an item (only if you're the owner).
    """
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    queryset = Item.objects.all().prefetch_related('categories', 'pictures')

    @swagger_auto_schema(operation_description="Delete an existing item by ID.")
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class GetAllCategoriesView(APIView):
    operation_description="Retrieve a list of all available categories."

    @swagger_auto_schema(
        operation_description="Retrieve all available categories.",
        responses={
            200: "Returned the list of categories successfully.",
            400: "Bad request: Invalid query or parameters.",
            401: "Unauthorized: Authentication credentials are required."
        }
    )
    def get(self, request, *args, **kwargs):
        all_categories = ItemCategory.objects.all()
        return Response(all_categories.values(), status=status.HTTP_200_OK)

