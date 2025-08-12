# chat/views.py
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import DirectThread, DirectMessage
from .serializers import DirectThreadSerializer, DirectMessageSerializer

User = get_user_model()

class MyThreadsView(generics.ListAPIView):
    serializer_class = DirectThreadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        u = self.request.user
        return DirectThread.objects.filter(models.Q(user1=u) | models.Q(user2=u)).order_by("-last_message_at", "-created_at")

class EnsureThreadView(APIView):
    """
    POST {"other_user_id": <int>}
    -> returns the existing or newly created DirectThread
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        me = request.user
        other_id = int(request.data.get("other_user_id", 0))
        if other_id == 0 or other_id == me.id:
            return Response({"detail": "Invalid other_user_id"}, status=400)
        try:
            other = User.objects.get(id=other_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=404)

        a, b = DirectThread.normalize_pair(me.id, other.id)
        thread, _ = DirectThread.objects.get_or_create(user1_id=a, user2_id=b)
        return Response(DirectThreadSerializer(thread).data, status=status.HTTP_200_OK)

class ThreadMessagesView(generics.ListAPIView):
    serializer_class = DirectMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        thread_id = self.kwargs["thread_id"]
        # ensure access control: requester must be participant
        return DirectMessage.objects.filter(
            thread_id=thread_id,
            thread__in=DirectThread.objects.filter(models.Q(user1=self.request.user) | models.Q(user2=self.request.user))
        ).select_related("sender")
