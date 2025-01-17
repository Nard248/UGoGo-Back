from rest_framework import generics, permissions
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.pagination import PageNumberPagination

from .models import Country, City, Airport, CityPolicy
from .serializers import CountrySerializer, CitySerializer, AirportSerializer, CityPolicySerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'page_size'
    max_page_size = 100

class CountryListCreateView(generics.ListCreateAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination

    @swagger_auto_schema( exclude = True,
        operation_description="Retrieve a list of all countries or create a new country.",
        responses={
            200: CountrySerializer(many=True),
            201: CountrySerializer(),
            400: "Bad Request - Invalid data",
            401: "Unauthorized",
        },
        request_body=CountrySerializer,
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    @swagger_auto_schema( exclude = True,
        operation_description="Retrieve a list of all countries.",
        responses={
            200: CountrySerializer(many=True),
            401: "Unauthorized",
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CountryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @swagger_auto_schema( exclude = True,
        operation_description="Retrieve details of a specific country.",
        responses={
            200: CountrySerializer(),
            404: "Not Found",
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema( exclude = True,
        operation_description="Update a specific country.",
        responses={
            200: CountrySerializer(),
            400: "Bad Request - Invalid data",
            401: "Unauthorized",
            404: "Not Found",
        },
        request_body=CountrySerializer,
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema( exclude = True,
        operation_description="Partially update a specific country.",
        responses={
            200: CountrySerializer(),
            400: "Bad Request - Invalid data",
            401: "Unauthorized",
            404: "Not Found",
        },
        request_body=CountrySerializer,
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema( exclude = True,
        operation_description="Delete a specific country.",
        responses={
            204: "No Content - Successfully deleted",
            401: "Unauthorized",
            404: "Not Found",
        },
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class CityListCreateView(generics.ListCreateAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @swagger_auto_schema( exclude = True,
        operation_description="Retrieve a list of all cities or create a new city.",
        responses={
            200: CitySerializer(many=True),
            201: CitySerializer(),
            400: "Bad Request - Invalid data",
            401: "Unauthorized",
        },
        request_body=CitySerializer,
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    @swagger_auto_schema( exclude = True,
        operation_description="Retrieve a list of all cities.",
        responses={
            200: CitySerializer(many=True),
            401: "Unauthorized",
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CityDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @swagger_auto_schema( exclude = True,
        operation_description="Retrieve details of a specific city.",
        responses={
            200: CitySerializer(),
            404: "Not Found",
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    #
    @swagger_auto_schema( exclude = True,
        operation_description="Update a specific city.",
        responses={
            200: CitySerializer(),
            400: "Bad Request - Invalid data",
            401: "Unauthorized",
            404: "Not Found",
        },
        request_body=CitySerializer,
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema( exclude = True,
        operation_description="Partially update a specific city.",
        responses={
            200: CitySerializer(),
            400: "Bad Request - Invalid data",
            401: "Unauthorized",
            404: "Not Found",
        },
        request_body=CitySerializer,
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema( exclude = True,
        operation_description="Delete a specific city.",
        responses={
            204: "No Content - Successfully deleted",
            401: "Unauthorized",
            404: "Not Found",
        },
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class AirportListCreateView(generics.ListCreateAPIView):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @swagger_auto_schema( exclude = True,
        operation_description="Retrieve a list of all airports or create a new airport.",
        responses={
            200: AirportSerializer(many=True),
            201: AirportSerializer(),
            400: "Bad Request - Invalid data",
            401: "Unauthorized",
        },
        request_body=AirportSerializer,
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    @swagger_auto_schema( exclude = True,
        operation_description="Retrieve a list of all airports.",
        responses={
            200: AirportSerializer(many=True),
            401: "Unauthorized",
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class AirportDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @swagger_auto_schema( exclude = True,
        operation_description="Retrieve details of a specific airport.",
        responses={
            200: AirportSerializer(),
            404: "Not Found",
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema( exclude = True,
        operation_description="Update a specific airport.",
        responses={
            200: AirportSerializer(),
            400: "Bad Request - Invalid data",
            401: "Unauthorized",
            404: "Not Found",
        },
        request_body=AirportSerializer,
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema( exclude = True,
        operation_description="Partially update a specific airport.",
        responses={
            200: AirportSerializer(),
            400: "Bad Request - Invalid data",
            401: "Unauthorized",
            404: "Not Found",
        },
        request_body=AirportSerializer,
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema( exclude = True,
        operation_description="Delete a specific airport.",
        responses={
            204: "No Content - Successfully deleted",
            401: "Unauthorized",
            404: "Not Found",
        },
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class CityPolicyListCreateView(generics.ListCreateAPIView):
    queryset = CityPolicy.objects.all()
    serializer_class = CityPolicySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @swagger_auto_schema( exclude = True,
        operation_description="Retrieve a list of all city policies or create a new city policy.",
        responses={
            200: CityPolicySerializer(many=True),
            201: CityPolicySerializer(),
            400: "Bad Request - Invalid data",
            401: "Unauthorized",
        },
        request_body=CityPolicySerializer,
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    @swagger_auto_schema( exclude = True,
        operation_description="Retrieve a list of all city policies.",
        responses={
            200: CityPolicySerializer(many=True),
            401: "Unauthorized",
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CityPolicyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CityPolicy.objects.all()
    serializer_class = CityPolicySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @swagger_auto_schema( exclude = True,
        operation_description="Retrieve details of a specific city policy.",
        responses={
            200: CityPolicySerializer(),
            404: "Not Found",
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema( exclude = True,
        operation_description="Update a specific city policy.",
        responses={
            200: CityPolicySerializer(),
            400: "Bad Request - Invalid data",
            401: "Unauthorized",
            404: "Not Found",
        },
        request_body=CityPolicySerializer,
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema( exclude = True,
        operation_description="Partially update a specific city policy.",
        responses={
            200: CityPolicySerializer(),
            400: "Bad Request - Invalid data",
            401: "Unauthorized",
            404: "Not Found",
        },
        request_body=CityPolicySerializer,
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema( exclude = True,
        operation_description="Delete a specific city policy.",
        responses={
            204: "No Content - Successfully deleted",
            401: "Unauthorized",
            404: "Not Found",
        },
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
