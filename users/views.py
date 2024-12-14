from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .serializers import RegisterUserSerializer, CustomUserSerializer
from .models import Users


class RegisterUserView(APIView):
    """
    Endpoint for registering a new user.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Register a new user.",
        request_body=RegisterUserSerializer,
        responses={
            201: "User registered successfully.",
            400: "Bad request - Validation error",
        }
    )
    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "User registered successfully.",
                "user": CustomUserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer for token pair (access and refresh tokens).
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        # Add additional user info to the response
        data["user"] = {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom view to handle login and JWT token issuance.
    """
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(
        operation_description="Obtain access and refresh tokens by providing valid credentials.",
        request_body=TokenObtainPairSerializer,
        responses={
            200: "Access and refresh tokens issued successfully.",
            401: "Unauthorized - Invalid credentials",
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

