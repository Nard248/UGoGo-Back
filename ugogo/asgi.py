# ugogo/asgi.py
import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ugogo.settings')

django_asgi_app = get_asgi_application()

from chat.middleware import JWTAuthMiddleware
import chat.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JWTAuthMiddleware(AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    )),
})
