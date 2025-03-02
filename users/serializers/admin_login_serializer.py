from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class AdminLoginSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        if not user.is_email_verified:
            raise serializers.ValidationError({"error": "Login failed. Email is not verified.", "is_email_verified": False})

        if not user.is_active:
            raise serializers.ValidationError({"error": "Login failed. User account is not active."})

        if not user.is_staff:
            raise serializers.ValidationError({"error": "Login failed. User is not an admin."})

        data["user"] = {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
        }
        return data
