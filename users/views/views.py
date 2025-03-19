from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import Users
from users.serializers.serializers import RegisterUserSerializer, CustomUserSerializer, CustomTokenObtainPairSerializer, \
    LogOutSerializer, SendResedPasswordLinkSerializer, EmailVerificationSerializer, ResendVerificationCodeSerializer
from users.swagger_schemas.login_schema import login_schema
from users.utils import send_verification_email

from rest_framework.decorators import permission_classes
from rest_framework import status
from django.db.models import Q
from drf_yasg import openapi
from django.core.paginator import Paginator

from items.permissions import IsAdmin

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
            # logger.error(f"Token validation failed: {e}")
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


class SendResedPasswordLink(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(exclude=True,
                         operation_description="Request a password reset link.",
                         request_body=SendResedPasswordLinkSerializer,
                         responses={
                             200: "Password reset link sent successfully.",
                             400: "Bad request - Validation error",
                         }
                         )
    def post(self, request):
        serializer = SendResedPasswordLinkSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.context['user']
            # reset_user_password()
            return Response({"message": "Password reset link sent successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswrod(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(exclude=True,
                         operation_description="Request a password reset link.",
                         request_body=SendResedPasswordLinkSerializer,
                         responses={
                             200: "Password reset link sent successfully.",
                             400: "Bad request - Validation error",
                         }
                         )
    def post(self, request):
        serializer = SendResedPasswordLinkSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.context['user']
            # reset_user_password()
            return Response({"message": "Password reset link sent successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationCodeView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(exclude=True,
                         operation_description="Request a password reset link.",
                         request_body=ResendVerificationCodeSerializer,
                         responses={
                             200: "Email was sent successfully.",
                             404: "There is no user registered with this email"
                         }
                         )
    def post(self, request):
        serializer = ResendVerificationCodeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = Users.objects.get(email=email)
                if not user:
                    return Response({"error": "There is no user registered with this email", "is_registered": False},
                                    status=status.HTTP_404_NOT_FOUND)
                try:
                    send_verification_email(user)
                except:
                    return Response({"error": "Failed to send email."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                user.code_expiration = timezone.now() + timezone.timedelta(minutes=10)
                user.save()
                return Response({"message": "Email was sent successfully."}, status=status.HTTP_200_OK)
            except Users.DoesNotExist:
                return Response({"error": "There is no user registered with this email"},
                                status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(exclude=True,
                         operation_description="Get user information.",
                         responses={
                             200: "User information retrieved successfully.",
                             404: "User not found."
                         }
                         )
    def get(self, request):
        user = request.user
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)


class UserListView(APIView):
    """
    Get list of all users - admin only access
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(
        operation_description="Get list of all users (admin only)",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Number of items per page",
                              type=openapi.TYPE_INTEGER),
            openapi.Parameter('passport_verification_status', openapi.IN_QUERY,
                              description="Filter by passport verification status",
                              type=openapi.TYPE_STRING, enum=["pending", "verified", "rejected", "all"]),
            openapi.Parameter('search', openapi.IN_QUERY, description="Search by email or name",
                              type=openapi.TYPE_STRING),
        ],
        responses={
            200: "List of users returned successfully",
            401: "Unauthorized - Authentication credentials were not provided",
            403: "Permission denied - User is not an admin"
        }
    )
    def get(self, request):
        page = int(request.query_params.get('page', 1))
        page_size = min(int(request.query_params.get('page_size', 10)), 100)  # Limit max page size
        passport_status = request.query_params.get('passport_verification_status', None)
        search_query = request.query_params.get('search', None)

        users_queryset = Users.objects.all().order_by('-date_joined')

        if passport_status and passport_status != 'all':
            users_queryset = users_queryset.filter(passport_verification_status=passport_status)

        if search_query:
            users_queryset = users_queryset.filter(
                Q(email__icontains=search_query) |
                Q(full_name__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query)
            )

        total_count = users_queryset.count()

        paginator = Paginator(users_queryset, page_size)
        page_obj = paginator.get_page(page)

        user_serializer = CustomUserSerializer(page_obj, many=True)

        results = []
        for user_data, user_obj in zip(user_serializer.data, page_obj):
            user_data['is_active'] = user_obj.is_active
            user_data['is_staff'] = user_obj.is_staff
            user_data['is_email_verified'] = user_obj.is_email_verified
            user_data['passport_verification_status'] = user_obj.passport_verification_status
            user_data['is_passport_uploaded'] = user_obj.is_passport_uploaded
            user_data['date_joined'] = user_obj.date_joined
            results.append(user_data)

        return Response({
            'results': results,
            'count': total_count,
            'total_pages': paginator.num_pages,
            'current_page': page
        })