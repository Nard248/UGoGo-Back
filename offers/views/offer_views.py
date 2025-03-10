from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, filters
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from offers.models import Offer
from offers.serializer.offer_serializer import OfferCreateSerializer, OfferSerializer
from offers.serializer.offer_unified_serializer import UnifiedOfferCreationSerializer
from offers.views.pegination_view import StandardResultsSetPagination


class CreateOfferAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create a new flight + user_flight + offer in one request, including multiple categories.",
        request_body=UnifiedOfferCreationSerializer,
        responses={
            201: "Offer created successfully.",
            400: "Bad Request - Invalid data",
            401: "Unauthorized",
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = UnifiedOfferCreationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            offer = serializer.save()
            return Response(
                {
                    "message": "The offer was successfully created.",
                    "offer_id": offer.id
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OfferDetailAPIView(APIView):
    queryset = Offer.objects.all()
    serializer_class = OfferCreateSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        exclude=True,
        operation_description="Retrieve detailed information about a specific flight offer.",
        responses={
            200: OfferCreateSerializer(),
            404: "Not Found",
            401: "Unauthorized",
        }
    )
    def get(self, request, pk, *args, **kwargs):
        if not isinstance(pk, int):
            return Response(
                {"error": "Invalid ID. 'pk' must be an integer."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            offer = Offer.objects.select_related("user_flight__user", "user_flight__flight").get(pk=pk)
            offer_data = OfferSerializer(offer, context={"request": request}).data
            return Response({"offer": offer_data}, status=status.HTTP_200_OK)
        except Offer.DoesNotExist:
            return Response({"error": "Offer not found."}, status=404)

    @swagger_auto_schema(exclude=True,
                         operation_description="Update a specific flight offer.",
                         request_body=OfferCreateSerializer,
                         responses={
                             200: OfferCreateSerializer(),
                             400: "Bad Request - Invalid data",
                             404: "Not Found",
                             401: "Unauthorized",
                         }
                         )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(exclude=True,
                         operation_description="Partially update a specific flight offer.",
                         request_body=OfferCreateSerializer,
                         responses={
                             200: OfferCreateSerializer(),
                             400: "Bad Request - Invalid data",
                             404: "Not Found",
                             401: "Unauthorized",
                         }
                         )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(exclude=True,
                         operation_description="Delete a specific flight offer.",
                         responses={
                             204: "No Content - Successfully deleted",
                             404: "Not Found",
                             401: "Unauthorized",
                         }
                         )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class OfferListCreateAPIView(generics.ListCreateAPIView):
    queryset = Offer.objects.all().order_by('price')
    serializer_class = OfferCreateSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'courier__email', 'user_flight__user__email']
    ordering_fields = ['price', 'available_weight', 'available_space']
    ordering = ['price']

    @swagger_auto_schema(exclude=True,
                         operation_description="Retrieve a paginated list of all offers or create a new offer.",
                         manual_parameters=[
                             openapi.Parameter('page', openapi.IN_QUERY, description="Page number",
                                               type=openapi.TYPE_INTEGER),
                             openapi.Parameter('page_size', openapi.IN_QUERY, description="Number of items per page",
                                               type=openapi.TYPE_INTEGER),
                             openapi.Parameter('ordering', openapi.IN_QUERY,
                                               description="Ordering of results. E.g., 'price', '-departure_datetime'",
                                               type=openapi.TYPE_STRING),
                         ],
                         responses={
                             200: OfferCreateSerializer(many=True),
                             201: OfferCreateSerializer(),
                             400: "Bad Request - Invalid data",
                             401: "Unauthorized",
                         }
                         )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    @swagger_auto_schema(exclude=True,
                         operation_description="Retrieve a paginated list of all offers.",
                         responses={
                             200: OfferCreateSerializer(many=True),
                             401: "Unauthorized",
                         }
                         )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class GetUserOffersView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OfferSerializer

    @swagger_auto_schema(
        operation_description="Retrieve a list of offers created by the authenticated user.",
        responses={
            200: OfferSerializer(many=True),
            401: "Unauthorized",
        }
    )
    def get(self, request, *args, **kwargs):
        # return
        user = request.user
        offers = Offer.objects.filter(courier=user)
        serializer = OfferSerializer(offers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)