from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from offers.serializer.offer_serializer import OfferSerializer
from offers.serializer.search_offer_serializer import OfferSearchSerializer
from offers.serializer.advanced_offer_search_serializer import AdvancedOfferSearchSerializer
from offers.models import Offer


class OfferSearchView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        exclude=False,
        query_serializer=OfferSearchSerializer,
        operation_description="Retrieve detailed information about a specific flight offer.",
        responses={
            200: OfferSearchSerializer(),
            404: "Not Found",
            401: "Unauthorized",
        }
    )
    def get(self, request, *args, **kwargs):
        serializer = OfferSearchSerializer(data=request.query_params)

        if serializer.is_valid():
            offers = serializer.search_offers()

            serialized_offers = OfferSerializer(offers, many=True)

            return Response(serialized_offers.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OfferGetAllView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Retrieve all offers.",
        responses={
            200: "Returned the list of offers successfully.",
            400: "Bad request.",
            401: "Unauthorized."
        }
    )
    def get(self, request, *args, **kwargs):
        offers = Offer.objects.all()
        serialized_offers = OfferSerializer(offers, many=True)
        return Response(serialized_offers.data, status=status.HTTP_200_OK)


class AdvancedOfferSearchView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        exclude=False,
        query_serializer=AdvancedOfferSearchSerializer,
        operation_description="Search offers with advanced filters",
        responses={
            200: OfferSerializer(many=True),
            400: "Bad Request",
        }
    )
    def get(self, request, *args, **kwargs):
        serializer = AdvancedOfferSearchSerializer(data=request.query_params)
        if serializer.is_valid():
            offers = serializer.search_offers()
            serialized_offers = OfferSerializer(offers, many=True)
            return Response(serialized_offers.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)