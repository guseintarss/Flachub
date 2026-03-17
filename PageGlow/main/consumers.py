"""
WebSocket consumers for PageGlow
"""
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer для realtime уведомлений
    
    Подключение:
        ws://localhost:8000/ws/notifications/
    
    Сообщения от клиента:
        - {"type": "mark_read", "notification_id": 123}
        - {"type": "mark_all_read"}
    
    Сообщения клиенту:
        - {"type": "notification", "data": {...}}
        - {"type": "count", "count": 5}
    """

    async def connect(self):
        """Подключение к WebSocket"""
        # Требуется авторизация
        if not self.scope["user"].is_authenticated:
            await self.close()
            return

        self.user = self.scope["user"]
        self.room_group_name = f"user_{self.user.id}"

        # Присоединяемся к группе пользователя
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"WebSocket: Пользователь {self.user.id} подключился")

        # Отправляем текущее количество непрочитанных
        count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'type': 'count',
            'count': count
        }))

    async def disconnect(self, close_code):
        """Отключение от WebSocket"""
        # Покидаем группу пользователя
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        logger.info(f"WebSocket: Пользователь отключился (code: {close_code})")

    async def receive(self, text_data):
        """Получение сообщения от клиента"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'mark_read':
                notification_id = data.get('notification_id')
                await self.mark_as_read(notification_id)
                
            elif message_type == 'mark_all_read':
                await self.mark_all_as_read()

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {text_data}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    async def send_notification(self, event):
        """
        Отправка уведомления клиенту
        
        Вызывается через channel_layer.group_send()
        """
        notification = event['notification']
        
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'data': notification
        }))

        # Обновляем счётчик
        count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'type': 'count',
            'count': count
        }))

    async def send_count_update(self, event):
        """
        Обновление счётчика уведомлений
        """
        count = event['count']
        
        await self.send(text_data=json.dumps({
            'type': 'count',
            'count': count
        }))

    @database_sync_to_async
    def get_unread_count(self):
        """Получить количество непрочитанных уведомлений"""
        from main.models import Notification
        return Notification.objects.filter(
            recipient=self.user,
            is_read=False
        ).count()

    @database_sync_to_async
    def mark_as_read(self, notification_id):
        """Отметить уведомление как прочитанное"""
        from main.models import Notification
        try:
            notification = Notification.objects.get(
                id=notification_id,
                recipient=self.user
            )
            notification.is_read = True
            notification.save()
        except Notification.DoesNotExist:
            pass

    @database_sync_to_async
    def mark_all_as_read(self):
        """Отметить все уведомления как прочитанные"""
        from main.models import Notification
        Notification.objects.filter(
            recipient=self.user,
            is_read=False
        ).update(is_read=True)


def send_notification_to_user(user_id, notification_data):
    """
    Утилита для отправки уведомления пользователю через Channels
    
    Использование:
        from main.consumers import send_notification_to_user
        send_notification_to_user(user.id, notification_data)
    """
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    
    channel_layer = get_channel_layer()
    room_group_name = f"user_{user_id}"
    
    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            'type': 'send_notification',
            'notification': notification_data
        }
    )


def send_count_update_to_user(user_id, count):
    """
    Утилита для обновления счётчика уведомлений
    
    Использование:
        send_count_update_to_user(user.id, count)
    """
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    
    channel_layer = get_channel_layer()
    room_group_name = f"user_{user_id}"
    
    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            'type': 'send_count_update',
            'count': count
        }
    )
