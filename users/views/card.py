# views.py
from datetime import datetime

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated
from ..models import BankCard, EmailVerificationCode
from ..serializers.bank_card_serializer import BankCardSerializer
from ..serializers.payout_serializer import PayOutSerializer
from ..utils import send_card_verification_email, check_verification_code


class PayOutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = PayOutSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        # All validations passed
        validated_data = serializer.validated_data
        user = request.user
        card_id = validated_data["card_id"]
        transfer_amount = validated_data["transfer_amount"]

        # Proceed with payout (e.g., make_payment(user, card_id, transfer_amount))

        return Response({"message": "Payment processed successfully."}, status=status.HTTP_200_OK)

class BankCardViewSet(APIView):
    serializer_class = BankCardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BankCard.objects.filter(user=self.request.user)

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Set the user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # NOT ALLOWED METHODS
    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PUT method is not allowed")

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PATCH method is not allowed")

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed("DELETE method is not allowed")


class SendCardVerificationEmailView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user

        existing_code = EmailVerificationCode.objects.filter(user=user, expires_at__gt=datetime.now()).first()
        if existing_code:
            return Response({"message": "You already have an active verification code."}, status=400)

        code_generator = EmailVerificationCode(user=user)


        send_card_verification_email(
            user=user,
            code_generator=code_generator
        )

        return Response({"message": "Verification email sent."}, status=200)