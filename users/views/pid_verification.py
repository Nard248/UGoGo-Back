from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.serializers.serializers import PIDUploadSerializer


class PIDUploadView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PIDUploadSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            pid = serializer.save()

            return Response({'message': f'PID {pid.id} uploaded successfully'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
