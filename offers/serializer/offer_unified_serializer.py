# offers/serializer/offer_unified_serializer.py

from rest_framework import serializers
from django.utils import timezone
from locations.models import Airport
from items.models.items import ItemCategory
from offers.models import Flight, UserFlight, Offer
from users.models import Users

class UnifiedOfferCreationSerializer(serializers.Serializer):
    """
    Single serializer to handle:
       - Creating a Flight
       - Creating a UserFlight
       - Creating an Offer with multiple categories
    """
    # Flight fields
    flight_number = serializers.CharField(required=True, max_length=50)
    from_airport_id = serializers.IntegerField()
    to_airport_id = serializers.IntegerField()
    departure_datetime = serializers.DateTimeField()
    arrival_datetime = serializers.DateTimeField()
    flight_details = serializers.CharField(required=False, allow_blank=True)
    publisher = serializers.CharField(required=False, default='airline')

    # Offer fields
    # We'll store categories via category_ids
    category_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    allow_fragile = serializers.BooleanField(required=False, default=False)
    available_dimensions = serializers.CharField(required=False, allow_blank=True)
    available_weight = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)
    available_space = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)
    price = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_from_airport_id(self, value):
        if not Airport.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Invalid from_airport_id.")
        return value

    def validate_to_airport_id(self, value):
        if not Airport.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Invalid to_airport_id.")
        return value

    def validate_category_ids(self, value):
        """
        Ensure every category ID is valid.
        You could also skip this if you handle missing categories gracefully.
        """
        for cat_id in value:
            if not ItemCategory.objects.filter(pk=cat_id).exists():
                raise serializers.ValidationError(f"Invalid category_id: {cat_id}")
        return value

    def create(self, validated_data):
        request_user = self.context['request'].user

        # pop out flight pieces
        from_airport_id = validated_data.pop('from_airport_id')
        to_airport_id = validated_data.pop('to_airport_id')

        from_airport = Airport.objects.get(pk=from_airport_id)
        to_airport = Airport.objects.get(pk=to_airport_id)

        flight_number = validated_data.pop('flight_number')
        publisher = validated_data.pop('publisher', 'airline')
        flight_details = validated_data.pop('flight_details', '')
        departure_datetime = validated_data.pop('departure_datetime')
        arrival_datetime = validated_data.pop('arrival_datetime')

        # Create the Flight
        flight_obj = Flight.objects.create(
            creator=request_user,
            flight_number=flight_number,
            publisher=publisher,
            from_airport=from_airport,
            to_airport=to_airport,
            departure_datetime=departure_datetime,
            arrival_datetime=arrival_datetime,
            details=flight_details
        )

        # Create the UserFlight
        user_flight_obj = UserFlight.objects.create(
            flight=flight_obj,
            user=request_user
        )

        # handle categories
        category_ids = validated_data.pop('category_ids', [])
        allow_fragile = validated_data.pop('allow_fragile', False)

        # If you want to add a "Fragile" category automatically:
        if allow_fragile:
            # Either get or create a "Fragile" category
            fragile_cat, created = ItemCategory.objects.get_or_create(
                name="Fragile",
                defaults={"description": "Fragile items that need special care"}
            )
            if fragile_cat.id not in category_ids:
                category_ids.append(fragile_cat.id)

        # Prepare Offer creation
        offer_data = {
            'user_flight': user_flight_obj,
            'courier': request_user,
            'allow_fragile': allow_fragile,
            'available_dimensions': validated_data.pop('available_dimensions', ''),
            'available_weight': validated_data.pop('available_weight'),
            'available_space': validated_data.pop('available_space'),
            'price': validated_data.pop('price'),
            'notes': validated_data.pop('notes', '')
        }

        offer_obj = Offer.objects.create(**offer_data)
        # Now set categories M2M
        if category_ids:
            cat_qs = ItemCategory.objects.filter(pk__in=category_ids)
            offer_obj.categories.set(cat_qs)

        return offer_obj
