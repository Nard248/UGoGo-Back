# chat/urls.py
from django.urls import path
from .views import MyThreadsView, EnsureThreadView, ThreadMessagesView

urlpatterns = [
    path("dm/threads/", MyThreadsView.as_view(), name="dm-my-threads"),
    path("dm/ensure-thread/", EnsureThreadView.as_view(), name="dm-ensure-thread"),
    path("dm/threads/<uuid:thread_id>/messages/", ThreadMessagesView.as_view(), name="dm-thread-messages"),
]
