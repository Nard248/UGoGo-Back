from rest_framework import serializers
from offers.models import Offer
from locations.models import Airport

class OfferSearchSerializer(serializers.Serializer):
    origin_airport = serializers.CharField(max_length=40, required=True)
    destination_airport = serializers.CharField(max_length=40, required=True)
    takeoff_date = serializers.DateField(required=True)


    class Meta:
        model = Offer
        fields = [
            'id', 'user_flight', 'user_flight_id', 'courier_id',
            'status', 'price',
            'available_weight', 'available_space'
        ]

    def validate_origin_airport(self, value):
        if not Airport.objects.filter(airport_code=value).exists():
            raise serializers.ValidationError("Invalid origin airport code.")
        return value

    def validate_destination_airport(self, value):
        if not Airport.objects.filter(airport_code=value).exists():
            raise serializers.ValidationError("Invalid destination airport code.")
        return value

    def validate_origin_destination_mismatch(self):
        origin_airport = self.validated_data.get('origin_airport')
        destination_airport = self.validated_data.get('destination_airport')
        if origin_airport == destination_airport:
            raise serializers.ValidationError("Origin and destination airports cannot be the same.")
        return destination_airport

    def search_offers(self):
        validated_data = self.validated_data
        origin_airport = validated_data['origin_airport']
        destination_airport = validated_data['destination_airport']
        takeoff_date = validated_data['takeoff_date']

        offers = Offer.objects.filter(
            user_flight__flight__from_airport__airport_code=origin_airport,
            user_flight__flight__to_airport__airport_code=destination_airport,
            user_flight__flight__departure_datetime__date=takeoff_date
        )
        return offers

class OfferGetAllSerializer(serializers.Serializer):
    class Meta:
        model = Offer
        fields = [
            'id', 'user_flight', 'user_flight_id', 'courier_id',
            'status', 'price',
            'available_weight', 'available_space'
        ]

    def search_offers(self):
        return Offer.objects.all()