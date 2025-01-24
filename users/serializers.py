from rest_framework import serializers
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
