from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from offers.serializer.search_offer_serializer import OfferSearchSerializer


class OfferSearchView(APIView):
    def get(self, request, *args, **kwargs):
        serializer = OfferSearchSerializer(data=request.data)
        if serializer.is_valid():
            offers = serializer.search_offers()
            return Response(offers, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)