from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterUserSerializer, CustomUserSerializer, CustomTokenObtainPairSerializer, \
    LogOutSerializer, PasswordResetSerializer, EmailVerificationSerializer
from .models import Users
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from django.utils import timezone



from .swagger_schemas.login_schema import login_schema
from .utils import send_verification_email


class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(exclude=True,
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
            user.is_active = False
            user.save()

            send_verification_email(user)
            return Response({
                "message": "User registered successfully. Please check your email to verify your account.",
                "user": CustomUserSerializer(user).data,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom view to handle login and JWT token issuance.
    """
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(exclude=True,
                         operation_description="Obtain access and refresh tokens by providing valid credentials.",
                         request_body=login_schema,
                         responses={
                             200: "Access and refresh tokens issued successfully.",
                             400: "Bad request - Email was not verified or user account is not active.",
                             401: "Unauthorized - Invalid credentials",
                         }
                         )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        return super().post(request, *args, **kwargs)


class LogOutView(APIView):
    """
    Custom endpoint for logging out users by blacklisting refresh tokens.
    """
    # Allow any user to access this endpoint
    permission_classes = [AllowAny]

    @swagger_auto_schema(exclude=True,
                         operation_description="Log out the user by blacklisting the given refresh token.",
                         request_body=LogOutSerializer,
                         responses={
                             200: "Successfully logged out.",
                             400: "Invalid refresh token or failed to blacklist.",
                         }
                         )
    def post(self, request):
        try:
            # Parse the refresh token from the request body
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "Refresh token is required for logout."}, status=status.HTTP_400_BAD_REQUEST)

            # Attempt to blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Invalid refresh token or failed to blacklist."},
                            status=status.HTTP_400_BAD_REQUEST)




class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    serializer_class = EmailVerificationSerializer
    @swagger_auto_schema(exclude=True,
                         operation_description="Verify the user's email with the provided verification code.",
                         request_body=EmailVerificationSerializer,
                         responses={
                             201: "Verification code was correct, account is active now",
                             400: "Bad request - Validation error",
                             404: "User with this email does not exist",
                             422: "Invalid verification code or verification code has expired",
                         }
                         )
    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email_verification_code = request.data.get('email_verification_code')
        email = request.data.get('email')

        if not email_verification_code or not email:
            return Response({"error": "Email and verification code are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = Users.objects.get(email=email)
        except Users.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

        if user.email_verification_code != email_verification_code:
            return Response({"error": "Invalid verification code."}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        if timezone.now() > user.code_expiration:
            return Response({"error": "Verification code has expired."}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        user.is_email_verified = True
        user.is_active = True
        user.save()

        return Response({"message": "Email verified successfully."}, status=status.HTTP_201_CREATED)

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(exclude=True,
                         operation_description="Request a password reset link.",
                         request_body=PasswordResetSerializer,
                         responses={
                             200: "Password reset link sent successfully.",
                             400: "Bad request - Validation error",
                         }
                         )
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password reset link sent successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)