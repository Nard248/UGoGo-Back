import re
from rest_framework import serializers
from decimal import Decimal

from items.models.items import Item, ItemCategory, ItemPicture
from items.models.request import Request
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
        fields = ['id', 'image_path']


class ItemSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    # For many-to-many categories, we can allow write with category_ids
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
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'user',
            'verified',    # can remain read-only if you only want admin to set, but you said no constraints
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
        user = self.context['request'].user
        validated_data['user'] = user

        item = super().create(validated_data)
        if category_ids:
            item.categories.set(category_ids)
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


# ---------------------------------------------
#  The "Unified" serializer for single endpoint
# ---------------------------------------------
class UnifiedItemPictureSerializer(serializers.Serializer):
    image_path = serializers.CharField()


class UnifiedItemSerializer(serializers.Serializer):
    """
    Serializer that collects all info to create
    an Item (with pictures, categories, pickup info).
    """
    name = serializers.CharField()
    weight = serializers.DecimalField(max_digits=10, decimal_places=2)
    dimensions = serializers.CharField()
    fragile = serializers.BooleanField(required=False, default=False)  # if you want a direct "is_fragile"
    description = serializers.CharField(required=False, allow_blank=True)
    pickup_name = serializers.CharField(required=False, allow_blank=True)
    pickup_surname = serializers.CharField(required=False, allow_blank=True)
    pickup_phone = serializers.CharField(required=False, allow_blank=True)
    pickup_email = serializers.EmailField(required=False, allow_blank=True)

    # For categories, we can accept IDs or names
    category_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )

    # For pictures
    pictures = UnifiedItemPictureSerializer(many=True, required=False)

    # If you want item state
    state = serializers.ChoiceField(
        choices=Item.STATE_CHOICES,
        required=False,
        default='draft'
    )

    def validate_dimensions(self, value):
        pattern = r'^\d+(\.\d+)?x\d+(\.\d+)?x\d+(\.\d+)?$'
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "Dimensions must be in the format 'LxWxH', e.g., '15x10x2'."
            )
        return value

    def validate_weight(self, value):
        if value <= 0:
            raise serializers.ValidationError("Weight must be positive.")
        return value

    def create(self, validated_data):
        # We manually create the Item + pictures + M2M categories
        category_ids = validated_data.pop('category_ids', [])
        pictures_data = validated_data.pop('pictures', [])
        fragile_flag = validated_data.pop('fragile', False)

        user = self.context['request'].user

        # We'll store "fragile" as a category or a separate field if you like
        # For now, let's say if "fragile" is True, we also add a "Fragile" category.
        # Or we store a separate boolean? For now let's do separate boolean: Let's assume
        # you want the "fragile" to become a Category. If you want a direct field, you can do that.
        # Here we do direct M2M approach:
        #    if fragile -> we create or find a category named "Fragile".
        #    if not -> do nothing extra
        if fragile_flag:
            fragile_cat, _ = ItemCategory.objects.get_or_create(
                name="Fragile",
                defaults={"description": "Items that are breakable or delicate"}
            )
            if fragile_cat.id not in category_ids:
                category_ids.append(fragile_cat.id)

        item = Item.objects.create(
            user=user,
            name=validated_data.get('name'),
            description=validated_data.get('description', ''),
            weight=validated_data.get('weight'),
            dimensions=validated_data.get('dimensions'),
            pickup_name=validated_data.get('pickup_name', ''),
            pickup_surname=validated_data.get('pickup_surname', ''),
            pickup_phone=validated_data.get('pickup_phone', ''),
            pickup_email=validated_data.get('pickup_email', ''),
            state=validated_data.get('state', 'draft'),
            # "verified" remains false by default
        )
        # Now set categories
        if category_ids:
            categories = ItemCategory.objects.filter(pk__in=category_ids)
            item.categories.set(categories)

        # Create pictures
        for pic in pictures_data:
            ItemPicture.objects.create(
                item=item,
                image_path=pic['image_path']
            )

        return item
