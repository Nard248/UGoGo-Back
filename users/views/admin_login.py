from rest_framework import serializers, status
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response

from users.serializers.admin_login_serializer import AdminLoginSerializer
from users.swagger_schemas.login_schema import login_schema


class AdminLoginView(TokenObtainPairView):
    """
    Custom view to handle login and JWT token issuance.
    """
    serializer_class = AdminLoginSerializer

    @swagger_auto_schema(exclude=True,
                         operation_description="Login for admin, only admin user can login via this endpoint.",
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
