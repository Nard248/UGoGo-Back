from rest_framework import generics, permissions
from .models import Item, Request
from .serializers import ItemSerializer, RequestSerializer
from .permissions import IsOwnerOrReadOnly, IsCourierOfOffer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


#
# -------------------- ITEM VIEWS --------------------
#

class ItemListCreateAPIView(generics.ListCreateAPIView):
    """
    GET (authenticated only): List all items of the user
    POST: Create a new item (owned by the request user)
    """
    serializer_class = ItemSerializer
    # Force authentication for BOTH list and create
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        # Only items belonging to the request user
        return Item.objects.filter(user=self.request.user).select_related('user')

    @swagger_auto_schema(
        operation_description="List all items for the authenticated user or create a new item.",
        responses={
            200: ItemSerializer(many=True),
            201: ItemSerializer(),
            401: "Unauthorized",
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new item (only for authenticated user).",
        request_body=ItemSerializer,
        responses={
            201: ItemSerializer(),
            400: "Bad Request",
            401: "Unauthorized",
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        # Assign the logged-in user as the owner
        serializer.save(user=self.request.user)


class ItemDestroyAPIView(generics.DestroyAPIView):
    """
    DELETE: Delete an item (owner only).
    """
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    queryset = Item.objects.all().select_related('user')

    @swagger_auto_schema(
        operation_description="Delete an item owned by the authenticated user.",
        responses={
            204: "No Content - Successfully deleted",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
        }
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


#
# -------------------- REQUEST VIEWS --------------------
#

class RequestCreateAPIView(generics.CreateAPIView):
    """
    POST: Create a new request to transport an item via a flight offer.
    """
    serializer_class = RequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create a new Request for an existing Offer and Item (sender-only).",
        request_body=RequestSerializer,
        responses={
            201: RequestSerializer(),
            400: "Bad Request - Invalid data",
            401: "Unauthorized",
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        # Make sure user is set on Request to avoid null user_id
        serializer.save(user=self.request.user)


class RequestUpdateStatusAPIView(generics.UpdateAPIView):
    """
    PATCH: Update the status of a request (only by the courier).
    """
    serializer_class = RequestSerializer
    queryset = Request.objects.all().select_related('offer__courier')
    permission_classes = [permissions.IsAuthenticated, IsCourierOfOffer]

    @swagger_auto_schema(
        operation_description="Update the status of a request (courier only).",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=['status']
        ),
        responses={
            200: RequestSerializer(),
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden - Not the courier",
            404: "Not Found",
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class RequestDestroyAPIView(generics.DestroyAPIView):
    """
    DELETE: Delete a request owned by the authenticated user.
    """
    serializer_class = RequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    queryset = Request.objects.all().select_related('item', 'offer', 'user')

    @swagger_auto_schema(
        operation_description="Delete a request owned by the authenticated user.",
        responses={
            204: "No Content - Successfully deleted",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
        }
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


#TODO Implement Get For Requests