from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from offers.serializer.offer_serializer import OfferSerializer
from offers.serializer.search_offer_serializer import OfferSearchSerializer


class OfferSearchView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        exclude=False,
        request_body=OfferSearchSerializer,
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