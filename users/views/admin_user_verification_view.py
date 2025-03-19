from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from items.permissions import IsAdmin
from users.serializers.admin_verification_serializers import VerifyUserPassportSerializer
from users.models import Users
from users.utils import send_passport_verification_sccuess_email, send_passport_verification_failed_email


class VerifyUserPassportView(APIView):
    permission_classes = [IsAdmin]
    serializer_class = VerifyUserPassportSerializer

    @swagger_auto_schema(
        operation_description="Verify user passport",
        request_body=VerifyUserPassportSerializer,
        responses={
            200: "User passport verified successfully.",
            400: "Bad request - Validation error",
        })
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            user = Users.get_user_by_id(validated_data["user_id"])
            if not user:
                return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)

            if not user.is_passport_uploaded:
                return Response({"message": f"User did not upload the passport photos"}, status=status.HTTP_400_BAD_REQUEST)

            if validated_data["is_passport_verified"]:
                user.set_passport_verification_status("verified")
                send_passport_verification_sccuess_email(user)

            if not validated_data["is_passport_verified"]:
                user.set_passport_verification_status("rejected")
                user.set_is_account_active(False)
                send_passport_verification_failed_email(user, validated_data["rejection_message"])


            return Response({"message": "User passport verified successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
