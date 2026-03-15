# 🔔 Realtime уведомления в PageGlow

## ✅ Что реализовано

Полноценная система realtime уведомлений на базе **Django Channels** и **WebSocket**:

- ✅ Мгновенные уведомления без перезагрузки страницы
- ✅ Счётчик непрочитанных уведомлений в реальном времени
- ✅ Toast уведомления при новых событиях
- ✅ Автоматическое переподключение при обрыве
- ✅ Поддержка темной темы
- ✅ Адаптивность для мобильных

## 📁 Типы уведомлений

| Событие | Описание | Получатель |
|---------|----------|------------|
| `like` | Кто-то лайкнул статью | Автор статьи |
| `comment` | Кто-то прокомментировал | Автор статьи |
| `follow` | Кто-то подписался | Автор |
| `new_post` | Новая статья от автора | Подписчики |

## 🚀 Запуск

### 1. Установка зависимостей

```bash
pip install channels[daphne]==4.2.0 channels-redis==4.2.0
```

### 2. Настройка Redis

Убедитесь что Redis запущен:

```bash
# Docker
docker run -d -p 6379:6379 redis:7-alpine

# Или локально
redis-server
```

### 3. Запуск Django с Channels

```bash
# Development
python manage.py runserver

# Production (Daphne)
daphne -b 0.0.0.0 -p 8000 PageGlow.asgi:application

# Production (Gunicorn with uvicorn workers)
gunicorn PageGlow.asgi:application -k uvicorn.workers.UvicornWorker
```

## 📁 Измененные файлы

### Backend

**PageGlow/settings.py:**
- Добавлен `'channels'` в INSTALLED_APPS
- Настроен `ASGI_APPLICATION`
- Настроен `CHANNEL_LAYERS` с Redis

**PageGlow/asgi.py:**
- ASGI application для WebSocket

**PageGlow/routing.py:**
- WebSocket URL routing

**main/consumers.py:**
- `NotificationConsumer` - WebSocket consumer
- `send_notification_to_user()` - утилита отправки

**main/views.py:**
- Интеграция отправки уведомлений для:
  - Лайков
  - Комментариев
  - Подписок
  - Новых статей

### Frontend

**main/static/main/js/notifications-ws.js:**
- WebSocket клиент
- Автопереподключение
- Toast уведомления
- Обновление счётчика

**main/static/main/css/app.css:**
- Стили для `.ws-notification-toast`

**templates/base.html:**
- Подключение JS клиента

## 🔧 Использование

### Отправка уведомления из кода

```python
from main.consumers import send_notification_to_user

# Создание уведомления в БД
notification = Notification.objects.create(
    recipient=user,
    sender=request.user,
    notification_type='like',
    post=post,
    message=f'{request.user.username} оценил вашу статью'
)

# Отправка через WebSocket
send_notification_to_user(user.id, {
    'id': notification.id,
    'message': notification.message,
    'type': notification.notification_type,
    'post_url': post.get_absolute_url(),
    'created_at': notification.created_at.isoformat()
})
```

### WebSocket сообщения

**От клиента к серверу:**
```javascript
// Отметить как прочитанное
socket.send(JSON.stringify({
    type: 'mark_read',
    notification_id: 123
}));

// Отметить все как прочитанные
socket.send(JSON.stringify({
    type: 'mark_all_read'
}));
```

**От сервера к клиенту:**
```javascript
// Новое уведомление
{
    "type": "notification",
    "data": {
        "id": 123,
        "message": "User liked your post",
        "type": "like",
        "post_url": "/post/my-article/",
        "created_at": "2026-03-15T10:30:00"
    }
}

// Обновление счётчика
{
    "type": "count",
    "count": 5
}
```

## 🎨 UI элементы

### Колокольчик уведомлений

Расположен в шапке сайта:
- 📊 Показывает количество непрочитанных
- 🔽 Выпадающий список с последними уведомлениями
- ✅ Кнопка "Прочитать все"

### Toast уведомления

Появляются при новых событиях:
- ⏱ Показываются 5 секунд
- 📱 Адаптивны для мобильных
- 🌓 Поддерживают темную тему

## 🔌 WebSocket API

### Подключение

```
ws://localhost:8000/ws/notifications/
```

Требуется авторизация через Django session authentication.

### Группы

Каждый пользователь подключается к группе `user_{user_id}`:

```python
# Отправка всем подключениям пользователя
await channel_layer.group_send(
    f"user_{user_id}",
    {
        'type': 'send_notification',
        'notification': notification_data
    }
)
```

## 🛠 Troubleshooting

### Ошибка подключения к WebSocket

Проверьте что:
1. Redis запущен
2. `CHANNEL_LAYERS` настроен правильно
3. ASGI application используется

```python
# Проверка CHANNEL_LAYERS
from channels.layers import get_channel_layer
layer = get_channel_layer()
print(layer)  # Должен быть RedisChannelLayer
```

### Уведомления не приходят

Проверьте логи:
```python
logger.error(f'Ошибка отправки WebSocket уведомления: {e}')
```

### Redis не доступен

Для development можно использовать in-memory layer:

```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}
```

⚠️ Не используйте in-memory в production!

## 📊 Мониторинг

### Подключенные WebSocket сессии

```python
from channels.layers import get_channel_layer

layer = get_channel_layer()
# Статистика доступна через Redis CLI
```

### Redis CLI

```bash
redis-cli
> KEYS *
> SMEMBERS channels:user_123
```

## 🔮 Будущие улучшения

- [ ] Уведомления о ответах на комментарии
- [ ] Упоминания (@username)
- [ ] Персонализация типов уведомлений
- [ ] Email дайджест
- [ ] Push уведомления (Service Workers)
- [ ] История уведомлений (API endpoint)

---

**Создано:** 2026-03-15  
**Статус:** ✅ Готово  
**Технологии:** Django Channels, WebSocket, Redis
