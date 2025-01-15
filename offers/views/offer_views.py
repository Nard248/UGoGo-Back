from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, filters
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from offers.models import Offer
from offers.serializer.flight_serializer import FlightSerializer
from offers.serializer.offer_serializer import OfferCreateSerializer, OfferSerializer
from offers.serializer.user_flight_serializer import UserFlightSerializer
from offers.swagger_schemas.offer_creation_schema import offer_creation_body_schema
from offers.views.pegination_view import StandardResultsSetPagination


class CreateOfferAPIView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(exclude=True,
                         operation_description="Create a new offer.",
                         request_body=offer_creation_body_schema,
                         responses={
                             200: "The offer was created successfully.",
                             400: "Bad Request - Invalid data",
                             404: "Not Found",
                             401: "Unauthorized",
                         }
                         )
    def post(self, request):

        flight_data = request.data.pop("flight_data", None)
        if not flight_data or not isinstance(flight_data, dict):
            return Response({"error": "Flight data is required."}, status=status.HTTP_400_BAD_REQUEST)

        flight_serializer = FlightSerializer(data=flight_data, context={"request": request})
        if flight_serializer.is_valid():
            new_flight = flight_serializer.save()
        else:
            return Response(
                {"error": "Flight creation failed. Not vaild data", "detailed error": flight_serializer.errors},
                status=status.HTTP_400_BAD_REQUEST)

        if not new_flight.id:
            return Response({"error": "Flight creation failed."}, status=status.HTTP_400_BAD_REQUEST)

        user_serializer = UserFlightSerializer(data={"flight_id": new_flight.id}, context={"request": request})
        if user_serializer.is_valid():
            new_user_flight = user_serializer.save()
        else:
            return Response({"error": "User Flight creation failed."}, status=status.HTTP_400_BAD_REQUEST)

        offer_data = request.data
        offer_data["user_flight_id"] = new_user_flight.id

        serializer = OfferCreateSerializer(data=offer_data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "The offer was successfully created."}, status=status.HTTP_201_CREATED)
        else:
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
            offer_serializer = OfferSerializer(offer, context={"request": request})
            return Response({"offer": offer_serializer}, status=status.HTTP_200_OK)
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
