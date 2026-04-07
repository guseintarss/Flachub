# Mobile API для PageGlow

REST API для мобильного приложения, построенное на Django REST Framework.

## Возможности

✅ **Полная CRUD для постов** - создание, чтение, обновление, удаление  
✅ **Комментарии** - с поддержкой вложенности и лайков  
✅ **Лайки и избранное** - для постов и комментариев  
✅ **Закладки и коллекции** - организация сохраненных статей  
✅ **Уведомления** - чтение и управление статусом  
✅ **Категории и теги** - навигация и фильтрация  
✅ **Загрузка медиа** - изображения для постов  
✅ **Пагинация, фильтрация, поиск** - эффективная работа с данными  
✅ **JWT авторизация** - безопасная аутентификация  

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Приложение уже добавлено в `INSTALLED_APPS` и URL подключен.

3. Запустите сервер:
```bash
python manage.py runserver
```

## Документация

Полная документация: [API_DOCS.md](./API_DOCS.md)

## Базовые эндпоинты

```
# Аутентификация
POST /auth/jwt/create/              # Получить JWT токен
POST /auth/jwt/refresh/             # Обновить токен

# Основные ресурсы
GET    /api/mobile/posts/           # Список постов
POST   /api/mobile/posts/           # Создать пост
GET    /api/mobile/posts/{id}/      # Детали поста
PUT    /api/mobile/posts/{id}/      # Обновить пост
DELETE /api/mobile/posts/{id}/      # Удалить пост

GET    /api/mobile/categories/      # Список категорий
GET    /api/mobile/tags/            # Список тегов

# Комментарии
GET    /api/mobile/posts/{id}/comments/     # Комментарии поста
POST   /api/mobile/posts/{id}/comments/     # Добавить комментарий

# Действия
POST   /api/mobile/post-actions/{id}/toggle_like/       # Лайк поста
POST   /api/mobile/post-actions/{id}/toggle_favorite/   # Избранное
POST   /api/mobile/comment-actions/{id}/toggle_like/    # Лайк комментария

# Уведомления
GET    /api/mobile/notifications/           # Список уведомлений
POST   /api/mobile/notifications/mark_all_read/  # Отметить все прочитанными
GET    /api/mobile/notifications/unread_count/   # Количество непрочитанных

# Закладки и коллекции
GET    /api/mobile/bookmarks/         # Мои закладки
POST   /api/mobile/bookmarks/         # Создать закладку
GET    /api/mobile/collections/       # Мои коллекции
POST   /api/mobile/collections/       # Создать коллекцию

# Пользователи
GET    /api/mobile/users/{id}/stats/        # Статистика пользователя
GET    /api/mobile/users/{id}/achievements/ # Достижения
GET    /api/mobile/users/{id}/posts/        # Посты пользователя

# Медиа
POST   /api/mobile/media/upload_image/  # Загрузить изображение
```

## Примеры использования

### Получение токена
```bash
curl -X POST http://localhost:8000/auth/jwt/create/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### Получение списка постов
```bash
curl http://localhost:8000/api/mobile/posts/ \
  -H "Authorization: Bearer <token>"
```

### Создание поста
```bash
curl -X POST http://localhost:8000/api/mobile/posts/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Мой пост",
    "content": "<p>Контент поста</p>",
    "post_type": "post",
    "cat": 1
  }'
```

### Лайк поста
```bash
curl -X POST http://localhost:8000/api/mobile/post-actions/1/toggle_like/ \
  -H "Authorization: Bearer <token>"
```

## Структура проекта

```
mobile_api/
├── __init__.py
├── apps.py                 # Конфигурация приложения
├── serializers.py          # DRF сериализаторы
├── views.py                # ViewSets и endpoints
├── urls.py                 # Роутинг
├── admin.py                # Админка
├── models.py               # Модели (используются из main)
├── tests.py                # Тесты
└── API_DOCS.md             # Полная документация API
```

## Зависимости

- Django 6.0.2
- Django REST Framework 3.16.1
- django-filter 24.3
- SimpleJWT 5.5.1
- Djoser 2.3.3

## Фильтрация и поиск

API поддерживает мощную фильтрацию:

```bash
# Поиск по заголовку и контенту
/api/mobile/posts/?search=django

# Фильтр по типу
/api/mobile/posts/?post_type=article

# Фильтр по категории
/api/mobile/posts/?cat=1

# Фильтр по тегу
/api/mobile/posts/?tag=python

# Фильтр по автору
/api/mobile/posts/?author=1

# Сортировка
/api/mobile/posts/?ordering=-views
/api/mobile/posts/?ordering=time_create
```

## Пагинация

Все списочные endpoints поддерживают пагинацию:

```json
{
  "count": 100,
  "next": "http://localhost:8000/api/mobile/posts/?page=2",
  "previous": null,
  "results": [...]
}
```

Размер страницы по умолчанию: 20  
Максимальный размер: 100  
Настройка: `?page_size=50`

## Безопасность

- JWT токены с expiration
- Throttling: 100 запросов/час (аноним), 1000/час (авторизованный)
- Валидация всех входных данных
- Мягкое удаление комментариев (is_active=False)
