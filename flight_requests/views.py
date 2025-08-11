import stripe
from rest_framework.generics import ListAPIView, CreateAPIView

from flight_requests.models.request import Request, RequestPayment
from flight_requests.serializers import RequestSerializer, FlightRequestActionSerializer, CreateRequestSerializer
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
                success_url='https://ugogo-test.azurewebsites.net/payment-success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url='https://ugogo-test.azurewebsites.net/payment-error'
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
            flight_request = Request.objects.get(id=request_id, requester=request.user)
        except Request.DoesNotExist:
            return Response({"error": "Request not found"}, status=status.HTTP_404_NOT_FOUND)

        if action == "accept":
            flight_request.status = 'in_progress'
        elif action == "reject":
            flight_request.status = "rejected"


        flight_request.save()



        return Response({
            "status": action,
            "message": f"Offer has been {action}",
            "offer": RequestSerializer(flight_request).data
        }, status=status.HTTP_200_OK)

