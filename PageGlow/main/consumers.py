"""
WebSocket consumers for PageGlow
"""
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)


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

    async def chat_message_notification(self, event):
        """
        Уведомление о новом сообщении в чате
        """
        await self.send(text_data=json.dumps({
            'type': 'new_chat_message',
            'chat_id': event['chat_id'],
            'chat_id_str': str(event['chat_id']),
            'sender': event['sender'],
            'text': event['text'],
        }))

        count = await self.get_unread_count()
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


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer для realtime чата

    Подключение:
        ws://localhost:8000/ws/chat/<chat_id>/

    Сообщения от клиента:
        - {"type": "send_message", "text": "Привет!"}
        - {"type": "mark_read"}

    Сообщения клиенту:
        - {"type": "new_message", "message": {...}}
        - {"type": "marked_read", "by_user": 1}
    """

    async def connect(self):
        if not self.scope["user"].is_authenticated:
            await self.close()
            return

        self.user = self.scope["user"]
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.room_group_name = f"chat_{self.chat_id}"

        if not await self.is_participant():
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"Chat WS: user {self.user.id} joined chat {self.chat_id}")

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            msg_type = data.get('type')

            if msg_type == 'send_message':
                text = data.get('text', '').strip()
                if text:
                    msg = await self.save_message(text)
                    if msg:
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                'type': 'chat_message',
                                'message': msg,
                            }
                        )

                        try:
                            other_ids = await self.get_other_participant_ids()
                            for other_id in other_ids:
                                await self.channel_layer.group_send(
                                    f'user_{other_id}',
                                    {
                                        'type': 'chat_message_notification',
                                        'chat_id': self.chat_id,
                                        'sender': self.user.username,
                                        'text': text[:100],
                                    }
                                )
                                await self.create_chat_notification(other_id, self.user, self.chat_id)
                        except Exception:
                            logger.exception('notify other user failed')

            elif msg_type == 'mark_read':
                count = await self.mark_messages_read()
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_marked_read',
                        'by_user': self.user.id,
                    }
                )

        except json.JSONDecodeError:
            logger.error(f"Chat WS: invalid JSON: {text_data}")
        except Exception as e:
            logger.error(f"Chat WS error: {e}")

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': event['message'],
        }))

    async def chat_marked_read(self, event):
        await self.send(text_data=json.dumps({
            'type': 'marked_read',
            'by_user': event['by_user'],
        }))

    @database_sync_to_async
    def is_participant(self):
        from main.models import Chat
        try:
            chat = Chat.objects.get(id=self.chat_id)
            return chat.participants.filter(id=self.user.id).exists()
        except Chat.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, text):
        from main.models import Chat, Message
        from django.utils import timezone
        try:
            chat = Chat.objects.get(id=self.chat_id)
            msg = Message.objects.create(chat=chat, sender=self.user, text=text)
            chat.last_message = text
            chat.last_message_time = msg.created_at
            chat.last_message_sender = self.user
            chat.save(update_fields=['last_message', 'last_message_time', 'last_message_sender', 'updated_at'])
            return {
                'id': msg.id,
                'sender': {
                    'id': self.user.id,
                    'username': self.user.username,
                    'avatar': self.user.photo.url if hasattr(self.user, 'photo') and self.user.photo else None,
                },
                'text': msg.text,
                'created_at': msg.created_at.isoformat(),
                'is_read': msg.is_read,
            }
        except Chat.DoesNotExist:
            return None

    @database_sync_to_async
    def get_other_participant_ids(self):
        from main.models import Chat
        try:
            chat = Chat.objects.get(id=self.chat_id)
            return list(chat.participants.exclude(id=self.user.id).values_list('id', flat=True))
        except Chat.DoesNotExist:
            return []

    @database_sync_to_async
    def create_chat_notification(self, recipient_id, sender, chat_id):
        from main.models import Notification
        Notification.objects.create(
            recipient_id=recipient_id,
            sender=sender,
            notification_type='chat_message',
            chat_id=chat_id,
            message=f'Новое сообщение от {sender.username}',
        )

    @database_sync_to_async
    def mark_messages_read(self):
        from main.models import Message
        return Message.objects.filter(
            chat_id=self.chat_id,
        ).exclude(
            sender=self.user
        ).filter(
            is_read=False
        ).update(is_read=True)


def send_chat_notification_to_user(user_id, chat_id, sender_username, text_preview):
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        from main.models import Notification, Chat
        from django.contrib.auth import get_user_model
        User = get_user_model()

        channel_layer = get_channel_layer()
        if channel_layer is None:
            return

        try:
            sender = User.objects.get(username=sender_username)
            Notification.objects.create(
                recipient_id=user_id,
                sender=sender,
                notification_type='chat_message',
                chat_id=chat_id,
                message=f'Новое сообщение от {sender_username}',
            )
        except Exception:
            pass

        async_to_sync(channel_layer.group_send)(
            f'user_{user_id}',
            {
                'type': 'chat_message_notification',
                'chat_id': chat_id,
                'sender': sender_username,
                'text': text_preview,
            }
        )
    except Exception:
        import logging
        logging.getLogger(__name__).exception('send_chat_notification failed')


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
