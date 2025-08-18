import json
from typing import Optional

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from .models import DirectThread, DirectMessage

User = get_user_model()

from urllib.parse import parse_qs
import logging


def _safe_parse_qs(scope) -> dict:
    raw = scope.get("query_string", b"")
    # Normalize robustly
    if isinstance(raw, (bytes, bytearray)):
        s = raw.decode("utf-8", "ignore")
    elif isinstance(raw, str):
        s = raw
    elif isinstance(raw, (list, tuple)) and raw:
        first = raw[0]
        if isinstance(first, (bytes, bytearray)):
            s = first.decode("utf-8", "ignore")
        else:
            s = str(first)
    else:
        s = ""
    return parse_qs(s, keep_blank_values=True)

class DirectDMConsumer(AsyncWebsocketConsumer):
    MAX_CONTENT_LEN = 4000

    async def connect(self):
        logging.warning("QS RAW type=%s value=%r", type(self.scope.get("query_string")), self.scope.get("query_string"))
        logging.warning("URL_ROUTE kwargs=%r", (self.scope.get("url_route") or {}).get("kwargs"))
        logging.warning("USER=%r is_auth=%r", self.scope.get("user"),
                        getattr(self.scope.get("user"), "is_authenticated", None))

        user = self.scope.get("user")
        if not user or isinstance(user, AnonymousUser) or not getattr(user, "is_authenticated", False):
            await self.close(code=4401)
            return

        self.me_id: int = user.id
        self.thread: Optional[DirectThread] = None

        kwargs = self.scope.get("url_route", {}).get("kwargs", {}) or {}
        thread_id = kwargs.get("thread_id")
        other_id = kwargs.get("other_id")

        if thread_id is not None:
            try:
                self.thread = await self._get_thread_if_member(int(thread_id), self.me_id)
            except (TypeError, ValueError):
                await self.close(code=4400)  # bad request
                return
        elif other_id is not None:
            try:
                self.thread = await self._ensure_thread_with_other(self.me_id, int(other_id))
            except (TypeError, ValueError):
                await self.close(code=4400)  # bad request
                return
        else:
            await self.close(code=4400)  # bad request
            return

        if not self.thread:
            await self.close(code=4403)
            return

        a, b = DirectThread.normalize_pair(self.thread.user1_id, self.thread.user2_id)
        self.group_name = f"dm_{a}_{b}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        # Accept either text JSON or raw bytes (utf-8)
        if bytes_data is not None and text_data is None:
            try:
                text_data = bytes_data.decode("utf-8")
            except Exception:
                return

        try:
            payload = json.loads(text_data or "{}")
        except json.JSONDecodeError:
            logging.error("Invalid JSON received: %s", text_data)
            return

        content = (payload.get("content") or "").strip()
        if not content:
            return

        if len(content) > self.MAX_CONTENT_LEN:
            content = content[: self.MAX_CONTENT_LEN]

        # Safety: ensure we have a thread
        if not getattr(self, "thread", None):
            await self.close(code=4400)
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
        if event["message"]["sender_id"] != self.me_id:
            await self.send(text_data=json.dumps(event["message"]))

    @database_sync_to_async
    def _get_thread_if_member(self, thread_id: int, me_id: int) -> Optional[DirectThread]:
        try:
            t = DirectThread.objects.get(id=thread_id)
            return t if me_id in (t.user1_id, t.user2_id) else None
        except DirectThread.DoesNotExist:
            return None

    @database_sync_to_async
    def _ensure_thread_with_other(self, me_id: int, other_id: int) -> Optional[DirectThread]:
        if me_id == other_id:
            return None
        # validate other exists
        if not User.objects.filter(id=other_id).exists():
            return None
        a, b = DirectThread.normalize_pair(me_id, other_id)
        t, _ = DirectThread.objects.get_or_create(user1_id=a, user2_id=b)
        return t

    @database_sync_to_async
    def _save_message(self, thread_id: int, me_id: int, content: str) -> DirectMessage:
        msg = DirectMessage.objects.create(thread_id=thread_id, sender_id=me_id, content=content)
        DirectThread.objects.filter(id=thread_id).update(last_message_at=msg.created_at)
        return msg
