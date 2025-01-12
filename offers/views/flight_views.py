from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_date
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, filters
from rest_framework import status
from rest_framework.response import Response

from .pegination_view import StandardResultsSetPagination
from ..models import Flight
from ..models import Offer
from ..serializer.flight_serializer import FlightSerializer
from ..serializer.offer_serializer import OfferSerializer


class FlightListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = FlightSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['publisher', 'from_airport__city__city_name', 'to_airport__city__city_name']
    ordering_fields = ['departure_datetime']

    @swagger_auto_schema( exclude = True,
        operation_description="Retrieve a paginated list of all available flight offers.",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Number of items per page",
                              type=openapi.TYPE_INTEGER),
            openapi.Parameter('ordering', openapi.IN_QUERY,
                              description="Ordering of results. E.g., 'departure_datetime', '-departure_datetime'",
                              type=openapi.TYPE_STRING),
        ],
        responses={
            200: FlightSerializer(many=True),
            401: "Unauthorized",
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema( exclude = True,
        operation_description="Create a new flight offer.",
        request_body=FlightSerializer,
        responses={
            201: FlightSerializer(),
            400: "Bad Request - Invalid data",
            401: "Unauthorized",
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class FlightDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @swagger_auto_schema( exclude = True,
        operation_description="Retrieve detailed information about a specific flight offer.",
        responses={
            200: FlightSerializer(),
            404: "Not Found",
            401: "Unauthorized",
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema( exclude = True,
        operation_description="Update a specific flight offer.",
        request_body=FlightSerializer,
        responses={
            200: FlightSerializer(),
            400: "Bad Request - Invalid data",
            404: "Not Found",
            401: "Unauthorized",
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema( exclude = True,
        operation_description="Partially update a specific flight offer.",
        request_body=FlightSerializer,
        responses={
            200: FlightSerializer(),
            400: "Bad Request - Invalid data",
            404: "Not Found",
            401: "Unauthorized",
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema( exclude = True,
        operation_description="Delete a specific flight offer.",
        responses={
            204: "No Content - Successfully deleted",
            404: "Not Found",
            401: "Unauthorized",
        }
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class FlightSearchAPIView(generics.ListAPIView):
    serializer_class = OfferSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = {
        'user_flight__flight__from_airport__city__city_name': ['exact', 'icontains'],
        'user_flight__flight__to_airport__city__city_name': ['exact', 'icontains'],
        'user_flight__flight__departure_datetime': ['gte', 'lte'],
        'price': ['gte', 'lte'],
        'available_weight': ['gte', 'lte'],
        'available_space': ['gte', 'lte'],
    }
    ordering_fields = ['price', 'user_flight__flight__departure_datetime', 'available_space']
    queryset = Offer.objects.all().order_by('user_flight__flight__departure_datetime')  # Added ordering

    @swagger_auto_schema( exclude = True,
        operation_description="Search for flight offers with specific criteria.",
        manual_parameters=[
            openapi.Parameter('origin', openapi.IN_QUERY, description="Origin city or airport name",
                              type=openapi.TYPE_STRING),
            openapi.Parameter('destination', openapi.IN_QUERY, description="Destination city or airport name",
                              type=openapi.TYPE_STRING),
            openapi.Parameter('departure_date_from', openapi.IN_QUERY, description="Departure date from (YYYY-MM-DD)",
                              type=openapi.TYPE_STRING),
            openapi.Parameter('departure_date_to', openapi.IN_QUERY, description="Departure date to (YYYY-MM-DD)",
                              type=openapi.TYPE_STRING),
            openapi.Parameter('min_weight', openapi.IN_QUERY, description="Minimum available weight",
                              type=openapi.TYPE_NUMBER),
            openapi.Parameter('max_weight', openapi.IN_QUERY, description="Maximum available weight",
                              type=openapi.TYPE_NUMBER),
            openapi.Parameter('min_price', openapi.IN_QUERY, description="Minimum price", type=openapi.TYPE_NUMBER),
            openapi.Parameter('max_price', openapi.IN_QUERY, description="Maximum price", type=openapi.TYPE_NUMBER),
            openapi.Parameter('ordering', openapi.IN_QUERY,
                              description="Ordering of results. E.g., 'price', '-departure_datetime'",
                              type=openapi.TYPE_STRING),
        ],
        responses={
            200: OfferSerializer(many=True),
            400: "Bad Request - Invalid query parameters",
            401: "Unauthorized",
        }
    )
    def get(self, request, *args, **kwargs):
        # Custom filtering based on query parameters
        origin = request.query_params.get('origin')
        destination = request.query_params.get('destination')
        departure_date_from = request.query_params.get('departure_date_from')
        departure_date_to = request.query_params.get('departure_date_to')
        min_weight = request.query_params.get('min_weight')
        max_weight = request.query_params.get('max_weight')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')

        queryset = self.get_queryset()

        try:
            if origin:
                queryset = queryset.filter(user_flight__flight__from_airport__city__city_name__icontains=origin)

            if destination:
                queryset = queryset.filter(user_flight__flight__to_airport__city__city_name__icontains=destination)

            if departure_date_from:
                parsed_date_from = parse_date(departure_date_from)
                if not parsed_date_from:
                    raise ValidationError(
                        {'departure_date_from': 'Invalid date format. It must be in YYYY-MM-DD format.'})
                queryset = queryset.filter(user_flight__flight__departure_datetime__date__gte=departure_date_from)

            if departure_date_to:
                parsed_date_to = parse_date(departure_date_to)
                if not parsed_date_to:
                    raise ValidationError(
                        {'departure_date_to': 'Invalid date format. It must be in YYYY-MM-DD format.'})
                queryset = queryset.filter(user_flight__flight__departure_datetime__date__lte=departure_date_to)

            if min_weight:
                queryset = queryset.filter(available_weight__gte=min_weight)

            if max_weight:
                queryset = queryset.filter(available_weight__lte=max_weight)

            if min_price:
                queryset = queryset.filter(price__gte=min_price)

            if max_price:
                queryset = queryset.filter(price__lte=max_price)
        except ValidationError as e:
            return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)

        return self.list(request, *args, **kwargs)
