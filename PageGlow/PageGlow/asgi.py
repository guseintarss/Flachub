"""
ASGI config for PageGlow project.

Exposes the ASGI callable in the manner specified by the 'uvicorn' server.
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PageGlow.settings')

django_asgi_app = get_asgi_application()

from PageGlow.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns),
    ),
})
