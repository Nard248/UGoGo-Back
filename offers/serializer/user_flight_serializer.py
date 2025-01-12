from offers.models import Flight, UserFlight
from offers.serializer.flight_serializer import FlightSerializer
from users.serializers import CustomUserSerializer
from rest_framework import serializers

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
            raise serializers.ValidationError("Authentication credentials were not provided. User Flight Serailizer")
        validated_data['user'] = user
        return super().create(validated_data)
