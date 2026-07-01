"""
WebSocket routing for PageGlow
"""
from django.urls import path
from main.consumers import NotificationConsumer, ChatConsumer

websocket_urlpatterns = [
    path('ws/notifications/', NotificationConsumer.as_asgi()),
    path('ws/chat/<int:chat_id>/', ChatConsumer.as_asgi()),
]
