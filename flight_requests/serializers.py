import stripe
from ugogo.settings import STRIPE_SECRET_KEY
from rest_framework import serializers

from flight_requests.models.request import Request, RequestPayment
stripe.api_key = STRIPE_SECRET_KEY

class RequestPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestPayment
        fields = ['payment_id', 'status', 'created_at']


class RequestSerializer(serializers.ModelSerializer):
    payment = RequestPaymentSerializer(read_only=True)

    class Meta:
        model = Request
        fields = ['id', 'item', 'offer', 'requester', 'comments', 'created_at', 'updated_at', 'payment']
        read_only_fields = ['id', 'requester', 'created_at', 'updated_at', 'payment']