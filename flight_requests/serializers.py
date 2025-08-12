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
    verification_code = serializers.SerializerMethodField()

    class Meta:
        model = Request
        fields = ['id', 'item', 'offer', 'requester', 'comments', 'created_at',
                  'updated_at', 'payment', 'status', 'verification_code']  # <- ADD 'verification_code'
        read_only_fields = ['id', 'requester', 'created_at', 'updated_at', 'payment', 'status']

    def get_verification_code(self, obj):
        """Show verification code to creator when request is created"""
        request = self.context.get('request')
        if not request or not request.user:
            return None

        # Only show to the requester (creator)
        if obj.requester == request.user:
            return obj.verification_code

        return None


class RequestSerializer(serializers.ModelSerializer):
    item = ItemSerializer()
    offer = OfferSerializer()
    payment = RequestPaymentSerializer(read_only=True)
    verification_code = serializers.SerializerMethodField()  # <- ADD THIS LINE

    class Meta:
        model = Request
        fields = ['id', 'item', 'offer', 'requester', 'comments', 'created_at',
                  'updated_at', 'payment', 'status', 'verification_code']  # <- ADD 'verification_code' HERE
        read_only_fields = ['id', 'requester', 'created_at', 'updated_at', 'payment',
                            'status']  # <- REMOVE 'verification_code' FROM HERE

    def get_verification_code(self, obj):
        """Show verification code to requester and courier (if accepted)"""
        request = self.context.get('request')
        if not request or not request.user:
            return None

        # Show to requester (sender)
        if obj.requester == request.user:
            return obj.verification_code

        # Show to courier only if request is accepted
        if (obj.status in ['accepted', 'in_process', 'completed'] and
                obj.offer.courier == request.user):
            return obj.verification_code

        return None

class FlightRequestActionSerializer(serializers.Serializer):
    request_id = serializers.IntegerField()
    action = serializers.ChoiceField(choices=['accept', 'reject'])
