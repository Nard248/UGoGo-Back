from rest_framework import serializers
from offers.models import Offer
from items.models.items import ItemCategory

class AdvancedOfferSearchSerializer(serializers.Serializer):
    origin_airport = serializers.CharField(max_length=40, required=False)
    destination_airport = serializers.CharField(max_length=40, required=False)

    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    departure_after = serializers.DateTimeField(required=False)
    departure_before = serializers.DateTimeField(required=False)
    arrival_after = serializers.DateTimeField(required=False)
    arrival_before = serializers.DateTimeField(required=False)

    categories = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_empty=True
    )

    weight = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    space = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    def validate_categories(self, value):
        for cat_id in value:
            if not ItemCategory.objects.filter(pk=cat_id).exists():
                raise serializers.ValidationError(f"Invalid category id {cat_id}")
        return value

    def search_offers(self):
        data = self.validated_data

        offers = Offer.objects.filter(
            status='available',
            courier__passport_verification_status='verified'
        )

        filter_map = {
            'origin_airport': 'user_flight__flight__from_airport__airport_code',
            'destination_airport': 'user_flight__flight__to_airport__airport_code',
            'min_price': 'price__gte',
            'max_price': 'price__lte',
            'departure_after': 'user_flight__flight__departure_datetime__gte',
            'departure_before': 'user_flight__flight__departure_datetime__lte',
            'arrival_after': 'user_flight__flight__arrival_datetime__gte',
            'arrival_before': 'user_flight__flight__arrival_datetime__lte',
            'weight': 'available_weight__gte',
            'space': 'available_space__gte',
        }

        filter_kwargs = {
            lookup: data[key]
            for key, lookup in filter_map.items()
            if data.get(key) is not None
        }

        offers = offers.filter(**filter_kwargs)

        if data.get('categories'):
            offers = offers.filter(categories__in=data['categories']).distinct()

        return offers.order_by('price', 'user_flight__flight__departure_datetime')