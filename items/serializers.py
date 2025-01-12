

from rest_framework import serializers
from offers.models import Offer
from .models import Item
from .models.request import Request
from offers.serializer.offer_serializer import OfferSerializer
from users.serializers import CustomUserSerializer
from decimal import Decimal

class ItemSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = Item
        fields = [
            'id',
            'user',
            'name',
            'description',
            'weight',
            'dimensions',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_weight(self, value):
        if value <= 0:
            raise serializers.ValidationError("Weight must be a positive value.")
        return value

    def validate_dimensions(self, value):
        import re
        # Regex to validate format "LxWxH" where L, W, H are positive numbers (integers or decimals)
        if not re.match(r'^\d+(\.\d+)?x\d+(\.\d+)?x\d+(\.\d+)?$', value):
            raise serializers.ValidationError("Dimensions must be in the format 'LxWxH', e.g., '15x10x2'.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class RequestSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    item = ItemSerializer(read_only=True)
    item_id = serializers.PrimaryKeyRelatedField(
        queryset=Item.objects.all(),
        source='item',
        write_only=True
    )
    offer = OfferSerializer(read_only=True)
    offer_id = serializers.PrimaryKeyRelatedField(
        queryset=Offer.objects.filter(status='available'),
        source='offer',
        write_only=True
    )

    class Meta:
        model = Request
        fields = [
            'id', 'item', 'item_id',
            'offer', 'offer_id',
            'user',  # read-only
            'suggested_price',
            'comments',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'item', 'offer', 'user', 'status', 'created_at', 'updated_at']

    def create(self, validated_data):
        """
        For POST /requests/, set user to the request.user if not supplied.
        """
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        For PATCH (partial update), only update fields that are present.
        But if 'item' or 'offer' are missing, don't blow up ownership checks.
        """
        return super().update(instance, validated_data)

    def validate_suggested_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Suggested price must be a positive value.")
        return value

    def validate(self, attrs):
        """
        Handles ownership, capacity checks, etc.
        Also handles partial updates (PATCH) so item/offer might not be in attrs at all.
        """
        request = self.context['request']
        tolerance = Decimal("0.001")

        # On partial update, we might not get 'item' or 'offer' in attrs, so fallback to self.instance
        # (if it's an existing Request).
        if self.instance:
            # partial update scenario
            item = attrs.get('item', self.instance.item)
            offer = attrs.get('offer', self.instance.offer)
        else:
            # normal create scenario
            item = attrs.get('item')
            offer = attrs.get('offer')

        errors = {}

        # Validate status choice (always do this check)
        valid_status_values = [choice[0] for choice in Request.STATUS_CHOICES]
        if 'status' in attrs and attrs['status'] not in valid_status_values:
            errors['status'] = f"Status must be one of {', '.join(valid_status_values)}."

        # Only if we are not updating only the status, do other checks
        if not (len(attrs) == 1 and 'status' in attrs and self.instance):
            # If user is PATCHing only status and not changing item or offer, item may be None if a new item wasn’t supplied:
            if item is None and self.instance:
                item = self.instance.item

            if offer is None and self.instance:
                offer = self.instance.offer


            # 3) Offer availability check
            if offer and offer.status != 'available':
                errors['offer_id'] = "Selected flight offer does not exist or is not available."

            # If we are creating/validating the entire request (as in POST), do capacity checks:
            # Only if item and offer are present
            if item and offer and offer.status == 'available':
                total_weight = offer.available_weight or Decimal("0")
                total_space = offer.available_space or Decimal("0")

                # Sum existing requests with statuses 'pending' or 'accepted'
                existing_requests = offer.requests.filter(status__in=['pending', 'accepted'])
                used_weight = sum(r.item.weight for r in existing_requests)
                used_space = sum(self.calculate_space(r.item.dimensions) for r in existing_requests)

                # If we haven't changed item, subtract old item usage if partial update
                if self.instance and self.instance.item and self.instance.item != item:
                    used_weight -= self.instance.item.weight
                    used_space -= self.calculate_space(self.instance.item.dimensions)

                # Check new total weight
                if (used_weight + item.weight) > total_weight + tolerance:
                    errors['weight'] = "The item's weight exceeds the available baggage weight."

                # Check new total space
                item_space = self.calculate_space(item.dimensions)
                if (used_space + item_space) > total_space + tolerance:
                    errors['dimensions'] = "The item's dimensions exceed the available baggage space."

        # The tests expect blank comments if omitted
        if not self.instance and 'comments' not in attrs:
            attrs['comments'] = ""

        # if we got any errors, raise them
        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    def calculate_space(self, dims):
        """
        Convert "LxWxH" -> float(L)*float(W)*float(H).
        """
        try:
            parts = dims.lower().split('x')
            if len(parts) != 3:
                raise ValueError("Dimensions must have exactly three parts separated by 'x'.")
            length, width, height = map(float, parts)
            return Decimal(length * width * height)
        except ValueError as e:
            raise serializers.ValidationError(
                {'dimensions': f"Invalid dimensions format: {e}"},
                code='invalid'
            )