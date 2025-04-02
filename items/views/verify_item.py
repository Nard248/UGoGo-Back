from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from items.models.items import Item
from items.permissions import IsAdmin
from items.serializers import ItemVerificationSerializer


class VerifyItemView(APIView):
    permission_classes = [IsAdmin]
    serializer_class = ItemVerificationSerializer

    @swagger_auto_schema(
        operation_description="Verify user passport",
        request_body=ItemVerificationSerializer,
        responses={
            200: "User passport verified successfully.",
            400: "Bad request - Validation error",
        })
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            item = Item.get_item_by_id(validated_data["item_id"])
            if not item:
                return Response({"message": "Item not found."}, status=status.HTTP_404_NOT_FOUND)

            if not item.is_pictures_uploaded:
                return Response({"message": "Item photos are not uploaded"}, status=status.HTTP_400_BAD_REQUEST)

            if validated_data["is_item_verified"]:
                item.set_verification_status("verified")
                # send_passport_verification_sccuess_email(user)

            if not validated_data["is_item_verified"]:
                item.set_verification_status("rejected")
                # send_passport_verification_failed_email(user, validated_data["message"])

            return Response({"message": "Item was verified successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
