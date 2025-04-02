from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView

from items.models.items import Item, ItemCategory
from items.models.request import Request
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


# ---------------------- Request Views ----------------------
class RequestListCreateAPIView(generics.ListCreateAPIView):
    """
    GET: List all requests (optionally filter by user or item)
    POST: Create a new request for an existing item & offer.
    """
    serializer_class = RequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = Request.objects.select_related('item', 'offer', 'user', 'offer__courier')
        item_id = self.request.query_params.get('item_id')
        user_id = self.request.query_params.get('user_id')
        if item_id:
            qs = qs.filter(item_id=item_id)
        if user_id:
            qs = qs.filter(user_id=user_id)
        return qs

    @swagger_auto_schema(operation_description="List all requests. Can filter by user_id & item_id.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Create a new request. The user must own the item.")
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class RequestUpdateStatusAPIView(generics.UpdateAPIView):
    """
    PATCH: Update the status of a request (only the courier of the Offer can do this).
    """
    serializer_class = RequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsCourierOfOffer]
    queryset = Request.objects.select_related('item', 'offer', 'user', 'offer__courier')

    @swagger_auto_schema(operation_description="Update the status of a request (courier only).")
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class RequestDestroyAPIView(generics.DestroyAPIView):
    """
    DELETE: A request can be deleted by the user who created it.
    """
    serializer_class = RequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    queryset = Request.objects.select_related('item', 'offer', 'user', 'offer__courier')

    @swagger_auto_schema(operation_description="Delete a request you own.")
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


# ---------------------- Unified Creation Endpoint ----------------------

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

