from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .models import Users

class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    last_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Users
        fields = ['email', 'full_name', 'first_name', 'last_name', 'password']

    def create(self, validated_data):
        user = Users.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data['full_name'],
            first_name=validated_data.get('first_name', None),
            last_name=validated_data.get('last_name', None)
        )
        return user

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer for token pair (access and refresh tokens).
    """

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        if not user.is_email_verified:
            raise serializers.ValidationError({"error": "Login failed. Email is not verified.", "is_email_verified": False})

        if not user.is_active:
            raise serializers.ValidationError({"error": "Login failed. User account is not active."})

        data["user"] = {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
        }
        return data


class LogOutSerializer(serializers.Serializer):
    """
    Serializer for the Logout request body.
    """
    refresh = serializers.CharField(help_text="The refresh token to be blacklisted.")


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = Users.objects.get(email=value)
        except Users.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    def save(self):
        request = self.context.get('request')
        email = self.validated_data['email']
        user = Users.objects.get(email=email)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        # Send email with the token and uid
        # send_password_reset_email(user, uid, token, request)

class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    email_verification_code = serializers.CharField()

class ResendVerificationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()