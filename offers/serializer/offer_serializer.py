from rest_framework import serializers

from offers.models import UserFlight, Offer
from offers.serializer.user_flight_serializer import UserFlightSerializer


class OfferCreateSerializer(serializers.ModelSerializer):
    user_flight = UserFlightSerializer(read_only=True)
    user_flight_id = serializers.PrimaryKeyRelatedField(
        queryset=UserFlight.objects.all(), source='user_flight', write_only=True
    )

    class Meta:
        model = Offer
        fields = [
            'id', 'user_flight', 'user_flight_id', 'courier_id',
            'status', 'price',
            'available_weight', 'available_space'
        ]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be a positive value.")
        return value

    def validate_available_weight(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Available weight must be a positive value.")
        return value

    def validate_available_space(self, value):
        if value is None or value <= 0:
            raise serializers.ValidationError("Available space must be a positive value.")
        return value

    def validate_user_flight(self, value):
        request = self.context.get('request')
        if request and request.user != value.user:
            raise serializers.ValidationError("You can only create offers for your own flights.")
        return value

    def create(self, validated_data):

        request = self.context.get('request')
        user = request.user if request else None
        if user is None or not user.is_authenticated:
            raise serializers.ValidationError("Authentication credentials were not provided. Offer Serializer")

        validated_data['courier'] = user
        return super().create(validated_data)


class OfferSerializer(serializers.ModelSerializer):
    user_flight = UserFlightSerializer(read_only=True)
    user_flight_id = serializers.PrimaryKeyRelatedField(
        queryset=UserFlight.objects.all(), source='user_flight', write_only=True
    )

    class Meta:
        model = Offer
        fields = [
            'id', 'user_flight', 'user_flight_id', 'courier_id',
            'status', 'price',
            'available_weight', 'available_space'
        ]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be a positive value.")
        return value

    def validate_available_weight(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Available weight must be a positive value.")
        return value

    def validate_available_space(self, value):
        if value is None or value <= 0:
            raise serializers.ValidationError("Available space must be a positive value.")
        return value

    def validate_user_flight(self, value):
        request = self.context.get('request')
        if request and request.user != value.user:
            raise serializers.ValidationError("You can only create offers for your own flights.")
        return value