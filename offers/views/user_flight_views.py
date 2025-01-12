from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, filters
from rest_framework import status
from rest_framework.response import Response

from .pegination_view import StandardResultsSetPagination
from ..models import UserFlight
from ..serializer.user_flight_serializer import UserFlightSerializer


class UserFlightListCreateAPIView(generics.ListCreateAPIView):
    queryset = UserFlight.objects.all().order_by('-publish_datetime')
    serializer_class = UserFlightSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['flight__publisher', 'user__email']
    ordering_fields = ['publish_datetime', 'flight__departure_datetime']

    @swagger_auto_schema( exclude = True,
        operation_description="Retrieve a paginated list of all user flights or create a new user flight.",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Number of items per page",
                              type=openapi.TYPE_INTEGER),
            openapi.Parameter('ordering', openapi.IN_QUERY,
                              description="Ordering of results. E.g., 'publish_datetime', '-publish_datetime'",
                              type=openapi.TYPE_STRING),
        ],
        responses={
            200: UserFlightSerializer(many=True),
            201: UserFlightSerializer(),
            400: "Bad Request - Invalid data",
            401: "Unauthorized",
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class UserFlightDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserFlight.objects.all()
    serializer_class = UserFlightSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @swagger_auto_schema( exclude = True,
        operation_description="Retrieve detailed information about a specific user flight.",
        responses={
            200: UserFlightSerializer(),
            404: "Not Found",
            401: "Unauthorized",
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema( exclude = True,
        operation_description="Update a specific user flight.",
        request_body=UserFlightSerializer,
        responses={
            200: UserFlightSerializer(),
            400: "Bad Request - Invalid data",
            404: "Not Found",
            401: "Unauthorized",
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema( exclude = True,
        operation_description="Partially update a specific user flight.",
        request_body=UserFlightSerializer,
        responses={
            200: UserFlightSerializer(),
            400: "Bad Request - Invalid data",
            404: "Not Found",
            401: "Unauthorized",
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema( exclude = True,
        operation_description="Delete a specific user flight.",
        responses={
            204: "No Content - Successfully deleted",
            404: "Not Found",
            401: "Unauthorized",
        }
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
