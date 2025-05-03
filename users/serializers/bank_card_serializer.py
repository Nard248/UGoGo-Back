from datetime import datetime

from rest_framework import serializers
from ..models import BankCard

class BankCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankCard
        fields = ['id', 'user', 'card_number', 'card_holder_name', 'expiration_date']

    def validate_expiration_date(self, value):
        current_date = datetime.now()
        month, year = map(int, value.split('/'))

        expiration_date = datetime(year=2000 + year, month=month, day=1)

        if expiration_date < current_date:
            raise serializers.ValidationError("The expiration date cannot be in the past.")

        return value