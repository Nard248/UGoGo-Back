import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from .models import DirectThread, DirectMessage

User = get_user_model()

class DirectDMConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
            await self.close(code=4401)  # unauthorized
            return

        self.me_id = user.id
        self.thread = None

        thread_id = self.scope["url_route"]["kwargs"].get("thread_id")
        other_id = self.scope["url_route"]["kwargs"].get("other_id")

        if thread_id:
            self.thread = await self._get_thread_if_member(thread_id, self.me_id)
        elif other_id:
            self.thread = await self._ensure_thread_with_other(self.me_id, int(other_id))
        else:
            await self.close(code=4400)  # bad request
            return

        if not self.thread:
            await self.close(code=4403)  # forbidden
            return

        a, b = DirectThread.normalize_pair(self.thread.user1_id, self.thread.user2_id)
        self.group_name = f"dm_{a}_{b}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        payload = json.loads(text_data or "{}")
        content = (payload.get("content") or "").strip()
        if not content:
            return
        msg = await self._save_message(self.thread.id, self.me_id, content)
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "dm.message",
                "message": {
                    "id": str(msg.id),
                    "thread": str(msg.thread_id),
                    "sender_id": msg.sender_id,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat(),
                },
            },
        )

    async def dm_message(self, event):
        await self.send(text_data=json.dumps(event["message"]))

    # ---------- DB helpers ----------
    @database_sync_to_async
    def _get_thread_if_member(self, thread_id, me_id):
        try:
            t = DirectThread.objects.get(id=thread_id)
            return t if me_id in (t.user1_id, t.user2_id) else None
        except DirectThread.DoesNotExist:
            return None

    @database_sync_to_async
    def _ensure_thread_with_other(self, me_id, other_id):
        if me_id == other_id:
            return None
        # validate other exists
        if not User.objects.filter(id=other_id).exists():
            return None
        a, b = DirectThread.normalize_pair(me_id, other_id)
        t, _ = DirectThread.objects.get_or_create(user1_id=a, user2_id=b)
        return t

    @database_sync_to_async
    def _save_message(self, thread_id, me_id, content):
        msg = DirectMessage.objects.create(thread_id=thread_id, sender_id=me_id, content=content)
        DirectThread.objects.filter(id=thread_id).update(last_message_at=msg.created_at)
        return msg
