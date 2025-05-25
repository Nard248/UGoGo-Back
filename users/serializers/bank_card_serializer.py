from datetime import datetime

from rest_framework import serializers
from ..models import BankCard
from datetime import datetime

class BankCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankCard
        fields = ['id', 'card_number', 'card_holder_name', 'expiration_date']

    def validate_expiration_date(self, value):
        current_date = datetime.now().date()
        expiration_date = value.date() if isinstance(value, datetime) else value

        if expiration_date < current_date:
            raise serializers.ValidationError("The expiration date cannot be in the past.")
        return value
