# views.py
from datetime import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated
from ..models import BankCard, EmailVerificationCode
from ..serializers.bank_card_serializer import BankCardSerializer
from ..utils import send_verification_email, send_card_verification_email


class BankCardViewSet(APIView):
    serializer_class = BankCardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BankCard.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        """Disable PUT requests (full update)"""
        raise MethodNotAllowed("PUT method is not allowed")

    def partial_update(self, request, *args, **kwargs):
        """Disable PATCH requests (partial update)"""
        raise MethodNotAllowed("PATCH method is not allowed")

    def destroy(self, request, *args, **kwargs):
        """Optionally disable DELETE requests"""
        raise MethodNotAllowed("DELETE method is not allowed")


class SendCardVerificationEmailView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user

        existing_code = EmailVerificationCode.objects.filter(user=user, expires_at__gt=datetime.now()).first()
        if existing_code:
            return Response({"message": "You already have an active verification code."}, status=400)

        code_generetor = EmailVerificationCode(user=user)


        send_card_verification_email(
            user=user,
            code_generator=code_generetor
        )

        return Response({"message": "Verification email sent."}, status=200)