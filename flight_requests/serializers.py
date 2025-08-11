import stripe

from items.serializers import ItemSerializer
from offers.serializer.offer_serializer import OfferSerializer
from ugogo.settings import STRIPE_SECRET_KEY
from rest_framework import serializers

from flight_requests.models.request import Request, RequestPayment
stripe.api_key = STRIPE_SECRET_KEY

class RequestPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestPayment
        fields = ['payment_id', 'status', 'created_at']


class CreateRequestSerializer(serializers.ModelSerializer):
    payment = RequestPaymentSerializer(read_only=True)
    class Meta:
        model = Request
        fields = ['id', 'item', 'offer', 'requester', 'comments', 'created_at', 'updated_at', 'payment', 'status']
        read_only_fields = ['id', 'requester', 'created_at', 'updated_at', 'payment', 'status']

class RequestSerializer(serializers.ModelSerializer):
    item = ItemSerializer()
    offer = OfferSerializer()
    payment = RequestPaymentSerializer(read_only=True)
    class Meta:
        model = Request
        fields = ['id', 'item', 'offer', 'requester', 'comments', 'created_at', 'updated_at', 'payment', 'status']
        read_only_fields = ['id', 'requester', 'created_at', 'updated_at', 'payment', 'status']

class FlightRequestActionSerializer(serializers.Serializer):
    request_id = serializers.IntegerField()
    action = serializers.ChoiceField(choices=['accept', 'reject'])


class PickupCodeValidationSerializer(serializers.Serializer):
    request_id = serializers.IntegerField()
    pickup_code = serializers.CharField(max_length=4, min_length=4)


class DeliveryCodeValidationSerializer(serializers.Serializer):
    request_id = serializers.IntegerField()
    delivery_code = serializers.CharField(max_length=4, min_length=4)
