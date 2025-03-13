from rest_framework import serializers

class VerifyUserPassportSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    is_passport_verified = serializers.BooleanField()
    rejection_message = serializers.CharField(allow_null=True, required=False)

    def validate(self, attrs):
        is_passport_verified = attrs.get("is_passport_verified")
        rejection_message = attrs.get("rejection_message")

        if is_passport_verified and rejection_message:
            raise serializers.ValidationError(
                {"rejection_message": "Rejection message must be null if passport is verified."}
            )

        if not is_passport_verified and not rejection_message:
            raise serializers.ValidationError(
                {"rejection_message": "Rejection message is required if passport is not verified."}
            )

        return attrs

