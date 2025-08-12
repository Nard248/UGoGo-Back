from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # option A: connect by thread id
    re_path(r"ws/chat/dm/thread/(?P<thread_id>[0-9a-f-]+)/$", consumers.DirectDMConsumer.as_asgi()),
    # option B: connect by other user id (auto-creates/uses thread)
    re_path(r"ws/chat/dm/user/(?P<other_id>\d+)/$", consumers.DirectDMConsumer.as_asgi()),
]
