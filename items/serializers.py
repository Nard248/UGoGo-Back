import re
from rest_framework import serializers
from decimal import Decimal

from items.models.items import Item, ItemCategory, ItemPicture
from flight_requests.models.request import Request
from offers.models import Offer
from offers.serializer.offer_serializer import OfferCreateSerializer
from users.serializers.serializers import CustomUserSerializer


class ItemCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory
        fields = ['id', 'name', 'description']


class ItemPictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemPicture
        fields = ['id', 'image']


class ItemSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    uploaded_pictures = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=True
    )
    categories = ItemCategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=ItemCategory.objects.all(),
        required=False,
        allow_null=True
    )

    pictures = ItemPictureSerializer(many=True, read_only=True)

    class Meta:
        model = Item
        fields = [
            'id', 'user',
            'name', 'description',
            'weight', 'dimensions',
            'verified', 'state',
            'pickup_name', 'pickup_surname',
            'pickup_phone', 'pickup_email',
            'categories', 'category_ids',
            'pictures',
            'uploaded_pictures',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'user',
            'verified',
            'created_at', 'updated_at'
        ]

    def validate_weight(self, value):
        if value <= 0:
            raise serializers.ValidationError("Weight must be a positive value.")
        return value

    def validate_dimensions(self, value):
        pattern = r'^\d+(\.\d+)?x\d+(\.\d+)?x\d+(\.\d+)?$'
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "Dimensions must be in the format 'LxWxH', e.g., '15x10x2'."
            )
        return value

    def create(self, validated_data):
        category_ids = validated_data.pop('category_ids', [])
        uploaded_pictures = validated_data.pop('uploaded_pictures', [])

        user = self.context['request'].user
        validated_data['user'] = user

        item = super().create(validated_data)

        if category_ids:
            item.categories.set(category_ids)

        for picture in uploaded_pictures:
            ItemPicture.objects.create(item=item, image=picture)

        return item

    def update(self, instance, validated_data):
        category_ids = validated_data.pop('category_ids', None)
        instance = super().update(instance, validated_data)
        if category_ids is not None:
            instance.categories.set(category_ids)
        return instance


class RequestSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    item = ItemSerializer(read_only=True)
    item_id = serializers.PrimaryKeyRelatedField(
        queryset=Item.objects.all(),
        source='item',
        write_only=True
    )
    offer = OfferCreateSerializer(read_only=True)
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
            'user',
            'suggested_price',
            'comments',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'item', 'offer', 'user', 'created_at', 'updated_at']

    def validate_suggested_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Suggested price must be a positive value.")
        return value

    def validate(self, attrs):
        request_method = self.context['request'].method
        if request_method == 'POST':
            item = attrs.get('item')
            if item.user != self.context['request'].user:
                raise serializers.ValidationError("You can only create requests for your own item.")
        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        if 'comments' not in validated_data:
            validated_data['comments'] = ""
        return super().create(validated_data)

class ItemVerificationSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    is_item_verified = serializers.BooleanField()
    rejection_message = serializers.CharField(allow_null=True, required=False)

    def validate(self, attrs):
        is_item_verified = attrs.get("is_item_verified")
        rejection_message = attrs.get("rejection_message")

        if is_item_verified and rejection_message:
            raise serializers.ValidationError(
                {"rejection_message": "Rejection message must be null if passport is verified."}
            )

        if not is_item_verified and not rejection_message:
            raise serializers.ValidationError(
                {"rejection_message": "Rejection message is required if passport is not verified."}
            )

        return attrs
