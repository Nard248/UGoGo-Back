from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Flight
from .serializers import FlightSerializer


class FlightList(APIView):
    """
    Handles listing all flights and creating a new flight.
    """

    @swagger_auto_schema(
        operation_description="Retrieve a list of all flights.",
        responses={200: FlightSerializer(many=True)}
    )
    def get(self, request):
        flights = Flight.objects.all()
        serializer = FlightSerializer(flights, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Create a new flight.",
        request_body=FlightSerializer,
        responses={
            201: "Flight created successfully",
            400: "Bad request - Validation error",
        }
    )
    def post(self, request):
        serializer = FlightSerializer(data=request.data)
        if serializer.is_valid():
            flight = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
