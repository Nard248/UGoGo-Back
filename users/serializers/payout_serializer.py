from rest_framework import serializers

from users.utils import check_verification_code


class PayOutSerializer(serializers.Serializer):
    verification_code = serializers.CharField()
    transfer_amount = serializers.FloatField(min_value=0.01)
    card_id = serializers.IntegerField()

    def validate_verification_code(self, value):
        user = self.context["request"].user
        try:
            check_verification_code(value, user)
        except Exception as e:
            raise serializers.ValidationError(str(e) or "Invalid or expired verification code.")
        return value

    def validate(self, data):
        user = self.context["request"].user

        if user.balance < data["transfer_amount"]:
            raise serializers.ValidationError({"transfer_amount": "Insufficient balance."})

        # Optional: validate card ownership
        # from .models import BankCard
        # if not BankCard.objects.filter(id=data["card_id"], user=user).exists():
        #     raise serializers.ValidationError({"card_id": "Card not found or not owned by user."})

        return data
