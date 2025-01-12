from locations.models import Airport
from locations.serializers import AirportSerializer
from offers.models import Flight
from rest_framework import serializers


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

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request else None
        if user is None or not user.is_authenticated:
            raise serializers.ValidationError("Authentication credentials were not provided. - Flight Serlizer")
        print(validated_data)
        validated_data['creator'] = user
        # validated_data['publisher'] = "airline"
        return super().create(validated_data)