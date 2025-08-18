# chat/middleware.py
from __future__ import annotations
from typing import Optional
from urllib.parse import parse_qs

from asgiref.sync import sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from django.utils.functional import LazyObject

from rest_framework_simplejwt.authentication import JWTAuthentication


class _ResolvedUser(LazyObject):
    def _setup(self):
        self._wrapped = AnonymousUser()


async def _get_user_from_bearer(token: str):
    """
    Validate JWT and return Django user (or None) using DRF SimpleJWT.
    """
    jwt_auth = JWTAuthentication()
    try:
        validated = jwt_auth.get_validated_token(token)
        # get_user() hits the DB; wrap in sync_to_async
        user = await sync_to_async(jwt_auth.get_user)(validated)
        return user
    except Exception:
        return None


def _extract_bearer_from_headers(scope) -> Optional[str]:
    # scope["headers"] is a list of (name, value) in bytes
    headers = dict(scope.get("headers") or [])
    raw = headers.get(b"authorization")
    if not raw:
        return None
    try:
        prefix, token = raw.decode().split(" ", 1)
    except ValueError:
        return None
    return token if prefix.lower() == "bearer" else None


def _extract_bearer_from_querystring(scope) -> Optional[str]:
    # Optional fallback: ws://.../?token=xxx
    query = scope.get("query_string", b"").decode()
    if not query:
        return None
    qs = parse_qs(query)
    vals = qs.get("token") or []
    return vals[0] if vals else None


class JWTAuthMiddleware(BaseMiddleware):
    """
    Channels middleware that authenticates WebSocket connections using
    'Authorization: Bearer <jwt>' (SimpleJWT).
    Also supports '?token=<jwt>' as a fallback.
    """

    async def __call__(self, scope, receive, send):
        scope = dict(scope)
        scope.setdefault("user", _ResolvedUser())

        token = _extract_bearer_from_headers(scope) or _extract_bearer_from_querystring(scope)
        if token:
            user = await _get_user_from_bearer(token)
            if user:
                scope["user"] = user

        return await super().__call__(scope, receive, send)
