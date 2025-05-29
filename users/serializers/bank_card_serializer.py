from datetime import datetime

from rest_framework import serializers
from ..models import BankCard
from datetime import datetime
import calendar

class BankCardSerializer(serializers.ModelSerializer):
    expiration_date = serializers.CharField()

    class Meta:
        model = BankCard
        fields = ['id', 'card_number', 'card_holder_name', 'expiration_date']

    def validate_expiration_date(self, value):
        current_date = datetime.now().date()
        if isinstance(value, str):
            try:
                parsed = datetime.strptime(value, "%m/%y")
                print(parsed)
                year = parsed.year
                month = parsed.month
                last_day = calendar.monthrange(year, month)[1]
                expiration_date = datetime(year, month, last_day).date()
                print(expiration_date)
            except ValueError:
                raise serializers.ValidationError("Expiration date must be in MM/YY format.")
        elif isinstance(value, datetime):
            expiration_date = value.date()
        elif isinstance(value, datetime.date):
            expiration_date = value
        else:
            raise serializers.ValidationError("Invalid expiration date format.")

        if expiration_date < current_date:
            raise serializers.ValidationError("The expiration date cannot be in the past.")

        self._validated_expiration_date = expiration_date
        return value

    def create(self, validated_data):
        validated_data['expiration_date'] = self._validated_expiration_date
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['expiration_date'] = self._validated_expiration_date
        return super().update(instance, validated_data)