# offers/serializers.py

from rest_framework import serializers

from locations.models import Airport
from users.models import Users
from .models import Flight, UserFlight, Offer
from locations.serializers import AirportSerializer
from users.serializers import CustomUserSerializer

class FlightSerializer(serializers.ModelSerializer):
    publisher_display = serializers.CharField(source='get_publisher_display', read_only=True)
    from_airport = AirportSerializer(read_only=True)
    to_airport = AirportSerializer(read_only=True)
    from_airport_id = serializers.PrimaryKeyRelatedField(
        queryset=Airport.objects.all(), source='from_airport', write_only=True
    )
    to_airport_id = serializers.PrimaryKeyRelatedField(
        queryset=Airport.objects.all(), source='to_airport', write_only=True
    )

    class Meta:
        model = Flight
        fields = [
            'id', 'publisher', 'publisher_display',
            'from_airport', 'from_airport_id',
            'to_airport', 'to_airport_id',
            'departure_datetime', 'arrival_datetime'
        ]

    def validate(self, attrs):
        unexpected_fields = set(self.initial_data.keys()) - set(self.fields.keys()) - {'from_airport_id', 'to_airport_id'}
        if unexpected_fields:
            raise serializers.ValidationError({
                'unexpected_fields': f"Received unexpected fields: {', '.join(unexpected_fields)}"
            })
        return attrs



class UserFlightSerializer(serializers.ModelSerializer):
    flight = FlightSerializer(read_only=True)
    flight_id = serializers.PrimaryKeyRelatedField(
        queryset=Flight.objects.all(), source='flight', write_only=True
    )
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = UserFlight
        fields = [
            'id', 'flight', 'flight_id',
            'user', 'publish_datetime'
        ]

    def create(self, validated_data):
        # Automatically assign the authenticated user
        request = self.context.get('request')
        user = request.user if request else None
        if user is None or not user.is_authenticated:
            raise serializers.ValidationError("Authentication credentials were not provided.")
        validated_data['user'] = user
        return super().create(validated_data)

class OfferSerializer(serializers.ModelSerializer):
    user_flight = UserFlightSerializer(read_only=True)
    user_flight_id = serializers.PrimaryKeyRelatedField(
        queryset=UserFlight.objects.all(), source='user_flight', write_only=True
    )
    courier = CustomUserSerializer(read_only=True)
    courier_id = serializers.PrimaryKeyRelatedField(
        queryset=Users.objects.all(), source='courier', write_only=True
    )

    class Meta:
        model = Offer
        fields = [
            'id', 'user_flight', 'user_flight_id',
            'courier', 'courier_id',
            'status', 'price',
            'available_weight', 'available_space'
        ]
