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
        offers = Offer.objects.filter(status='available', courier__passport_verification_status='verified')

        if data.get('origin_airport'):
            offers = offers.filter(user_flight__flight__from_airport__airport_code=data['origin_airport'])
        if data.get('destination_airport'):
            offers = offers.filter(user_flight__flight__to_airport__airport_code=data['destination_airport'])
        if data.get('min_price') is not None:
            offers = offers.filter(price__gte=data['min_price'])
        if data.get('max_price') is not None:
            offers = offers.filter(price__lte=data['max_price'])
        if data.get('departure_after'):
            offers = offers.filter(user_flight__flight__departure_datetime__gte=data['departure_after'])
        if data.get('departure_before'):
            offers = offers.filter(user_flight__flight__departure_datetime__lte=data['departure_before'])
        if data.get('arrival_after'):
            offers = offers.filter(user_flight__flight__arrival_datetime__gte=data['arrival_after'])
        if data.get('arrival_before'):
            offers = offers.filter(user_flight__flight__arrival_datetime__lte=data['arrival_before'])
        if data.get('weight') is not None:
            offers = offers.filter(available_weight__gte=data['weight'])
        if data.get('space') is not None:
            offers = offers.filter(available_space__gte=data['space'])
        if data.get('categories'):
            offers = offers.filter(categories__in=data['categories']).distinct()

        return offers.order_by('price', 'user_flight__flight__departure_datetime')
