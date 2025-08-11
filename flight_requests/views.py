import stripe
from django.utils import timezone
from rest_framework.generics import ListAPIView, CreateAPIView

from flight_requests.models.request import Request, RequestPayment
from flight_requests.serializers import (
    RequestSerializer,
    FlightRequestActionSerializer,
    CreateRequestSerializer,
    PickupCodeValidationSerializer,
    DeliveryCodeValidationSerializer,
)
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

class UserRequestListView(ListAPIView):
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Request.objects.select_related('item', 'offer').filter(offer__user_flight__user=self.request.user)

class CreateRequestView(CreateAPIView):
    serializer_class = CreateRequestSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if request.user.passport_verification_status != 'verified':
            return Response(
                {"error": "Passport not verified."},
                status=status.HTTP_403_FORBIDDEN
            )

        flight_request = serializer.save(requester=request.user)

        offer = flight_request.offer


        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f'Flight Offer #{str(offer.user_flight.flight)}',
                            'description': f'{offer.user_flight.flight}',
                        },
                        'unit_amount': int(offer.price * 100),  # integer in cents
                    },
                    'quantity': 1,
                }],
                mode='payment',
                metadata={'request_id': str(flight_request.id)},
                success_url='http://192.168.11.54:3000/payment-success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url='http://192.168.11.54:3000/payment-error'
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Return both the request data and the Stripe checkout URL
        response_data = serializer.data
        response_data['checkout_url'] = session.url
        return Response(response_data, status=status.HTTP_201_CREATED)

class ConfirmStripeSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        session_id = request.data.get("session_id")

        if not session_id:
            return Response({"error": "Missing session_id"}, status=400)

        try:
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == "paid":
                request_id = session.metadata.get('request_id')
                if request_id:
                    try:
                        flight_request = Request.objects.get(id=request_id, requester=request.user)
                        RequestPayment.objects.update_or_create(
                            request=flight_request,
                            defaults={
                                "payment_id": session.payment_intent,
                                "status": "paid"
                            }
                        )
                        flight_request.save()
                    except Request.DoesNotExist:
                        return Response({"error": "Request not found"}, status=404)

                return Response({"status": "success", "message": "Payment confirmed"})
            else:
                return Response({"status": "pending", "message": "Payment not completed yet"})
        except Exception as e:
            return Response({"error": str(e)}, status=500)



class FlightRequestActionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Deserialize the incoming data
        serializer = FlightRequestActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Extract validated data
        request_id = serializer.validated_data['request_id']
        action = serializer.validated_data['action']

        try:
            flight_request = Request.objects.get(
                id=request_id, offer__user_flight__user=request.user
            )
        except Request.DoesNotExist:
            return Response({"error": "Request not found"}, status=status.HTTP_404_NOT_FOUND)

        if action == "accept":
            from flight_requests.utils import generate_verification_code

            flight_request.pickup_verification_code = generate_verification_code('pickup')
            flight_request.pickup_code_generated_at = timezone.now()
            flight_request.status = 'in_process'
        elif action == "reject":
            flight_request.status = "rejected"

        flight_request.save()



        return Response({
            "status": action,
            "message": f"Offer has been {action}",
            "offer": RequestSerializer(flight_request).data
        }, status=status.HTTP_200_OK)


class GetPickupCodeView(APIView):
    """Sender retrieves Code 1 to give item to courier"""
    permission_classes = [IsAuthenticated]

    def get(self, request, request_id):
        try:
            flight_request = Request.objects.get(
                id=request_id,
                requester=request.user,
                status='in_process'
            )
        except Request.DoesNotExist:
            return Response({"error": "Request not found"}, status=404)

        return Response({
            "pickup_code": flight_request.pickup_verification_code,
            "stage": "pickup",
            "instructions": "Provide this code to the courier when handing over your item",
            "courier_info": {
                "name": flight_request.offer.user_flight.user.get_full_name(),
                "email": flight_request.offer.user_flight.user.email,
            },
        })


class ValidatePickupCodeView(APIView):
    """Courier validates Code 1 when receiving item from sender"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PickupCodeValidationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        request_id = serializer.validated_data['request_id']
        provided_code = serializer.validated_data['pickup_code']

        try:
            flight_request = Request.objects.get(
                id=request_id,
                offer__user_flight__user=request.user,
                status='in_process',
            )
        except Request.DoesNotExist:
            return Response({"error": "Request not found"}, status=404)

        flight_request.pickup_verification_attempts += 1

        if provided_code != flight_request.pickup_verification_code:
            flight_request.save()
            remaining = (
                flight_request.max_verification_attempts -
                flight_request.pickup_verification_attempts
            )
            return Response({
                "error": "Invalid pickup code",
                "remaining_attempts": remaining,
            }, status=400)

        from flight_requests.utils import generate_verification_code

        flight_request.pickup_code_verified = True
        flight_request.pickup_code_verified_at = timezone.now()
        flight_request.delivery_verification_code = generate_verification_code('delivery')
        flight_request.delivery_code_generated_at = timezone.now()
        flight_request.status = 'in_transit'
        flight_request.save()

        return Response({
            "status": "success",
            "message": "Item successfully received from sender. Ready for delivery.",
            "next_stage": "delivery",
        })


class GetDeliveryCodeView(APIView):
    """Sender retrieves Code 2 to share with pickup person"""
    permission_classes = [IsAuthenticated]

    def get(self, request, request_id):
        try:
            flight_request = Request.objects.get(
                id=request_id,
                requester=request.user,
                status='in_transit',
            )
        except Request.DoesNotExist:
            return Response({"error": "Request not found or item not yet picked up"}, status=404)

        return Response({
            "delivery_code": flight_request.delivery_verification_code,
            "stage": "delivery",
            "instructions": "Share this code with your pickup person. They will provide it to the courier.",
            "pickup_person": {
                "name": f"{flight_request.item.pickup_name} {flight_request.item.pickup_surname}",
                "phone": flight_request.item.pickup_phone,
                "email": flight_request.item.pickup_email,
            },
        })


class ValidateDeliveryCodeView(APIView):
    """Courier validates Code 2 when delivering item to pickup person"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DeliveryCodeValidationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        request_id = serializer.validated_data['request_id']
        provided_code = serializer.validated_data['delivery_code']

        try:
            flight_request = Request.objects.get(
                id=request_id,
                offer__user_flight__user=request.user,
                status='in_transit',
            )
        except Request.DoesNotExist:
            return Response({"error": "Request not found"}, status=404)

        flight_request.delivery_verification_attempts += 1

        if provided_code != flight_request.delivery_verification_code:
            flight_request.save()
            remaining = (
                flight_request.max_verification_attempts -
                flight_request.delivery_verification_attempts
            )
            return Response({
                "error": "Invalid delivery code",
                "remaining_attempts": remaining,
            }, status=400)

        flight_request.delivery_code_verified = True
        flight_request.delivery_code_verified_at = timezone.now()
        flight_request.status = 'completed'
        flight_request.save()

        return Response({
            "status": "success",
            "message": "Delivery completed successfully!",
            "completed_at": flight_request.delivery_code_verified_at,
        })

