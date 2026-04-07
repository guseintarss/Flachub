# Mobile API Документация

## Базовый URL
```
/api/mobile/
```

## Аутентификация
API использует JWT токены (через Djoser). 

### Получение токена
```
POST /auth/jwt/create/
Body:
{
  "email": "user@example.com",
  "password": "password123"
}

Response:
{
  "access": "<token>",
  "refresh": "<token>"
}
```

### Использование токена
Все защищенные endpoints требуют заголовок:
```
Authorization: Bearer <access_token>
```

---

## ОсновныеEndpoints

### 📝 Посты

#### Список постов
```
GET /api/mobile/posts/
Query params:
  - page: номер страницы
  - page_size: размер страницы (макс 100)
  - post_type: post|article|news|idea
  - cat: ID категории
  - tag: slug тега
  - author: ID автора
  - search: поиск по заголовку/контенту
  - ordering: -time_create|time_create|views|title

Response:
{
  "count": 100,
  "next": "url",
  "previous": null,
  "results": [PostListSerializer, ...]
}
```

#### Детали поста
```
GET /api/mobile/posts/{id}/
Response: PostDetailSerializer
```

#### Создание поста
```
POST /api/mobile/posts/
Auth: Required
Body:
{
  "title": "Заголовок",
  "content": "HTML контент",
  "post_type": "post",
  "cat": 1,
  "tags": [1, 2],
  "is_published": true
}
```

#### Обновление поста
```
PUT/PATCH /api/mobile/posts/{id}/
Auth: Required (только автор)
```

#### Удаление поста
```
DELETE /api/mobile/posts/{id}/
Auth: Required (только автор)
```

---

### 🏷️ Категории

#### Список категорий
```
GET /api/mobile/categories/
Response: [CategorySerializer, ...]
```

#### Детали категории
```
GET /api/mobile/categories/{slug}/
Response: CategorySerializer
```

---

### 🏷️ Теги

#### Список тегов
```
GET /api/mobile/tags/
Response: [TagSerializer, ...]
```

#### Детали тега
```
GET /api/mobile/tags/{slug}/
Response: TagSerializer
```

---

### 💬 Комментарии

#### Список комментариев поста
```
GET /api/mobile/posts/{post_id}/comments/
Query params:
  - page
  - page_size

Response: [CommentSerializer, ...]
```

#### Создание комментария
```
POST /api/mobile/posts/{post_id}/comments/
Auth: Required
Body:
{
  "content": "Текст комментария",
  "parent": null  // ID родительского комментария (для ответов)
}
```

#### Обновление комментария
```
PUT/PATCH /api/mobile/comments/{id}/
Auth: Required (только автор)
```

#### Удаление комментария
```
DELETE /api/mobile/comments/{id}/
Auth: Required (только автор)
```

---

### ❤️ Лайки и Избранное

#### Лайк поста
```
POST /api/mobile/post-actions/{post_id}/toggle_like/
Auth: Required
Response:
{
  "liked": true,
  "likes_count": 15
}
```

#### Избранное поста
```
POST /api/mobile/post-actions/{post_id}/toggle_favorite/
Auth: Required
Response:
{
  "favorited": true,
  "favorites_count": 8
}
```

#### Лайк комментария
```
POST /api/mobile/comment-actions/{comment_id}/toggle_like/
Auth: Required
Response:
{
  "liked": true,
  "likes_count": 5
}
```

---

### 🔔 Уведомления

#### Список уведомлений
```
GET /api/mobile/notifications/
Auth: Required
Response: [NotificationSerializer, ...]
```

#### Отметить прочитанным
```
POST /api/mobile/notifications/{id}/mark_read/
Auth: Required
```

#### Отметить все прочитанными
```
POST /api/mobile/notifications/mark_all_read/
Auth: Required
```

#### Количество непрочитанных
```
GET /api/mobile/notifications/unread_count/
Auth: Required
Response:
{
  "unread_count": 5
}
```

---

### 🔖 Закладки

#### Список закладок
```
GET /api/mobile/bookmarks/
Auth: Required
Response: [BookmarkSerializer, ...]
```

#### Создать закладку
```
POST /api/mobile/bookmarks/
Auth: Required
Body:
{
  "post": 1,
  "collection": 2,  // опционально
  "notes": "Заметка"
}
```

#### Удалить закладку
```
DELETE /api/mobile/bookmarks/{id}/
Auth: Required
```

---

### 📁 Коллекции

#### Список коллекций
```
GET /api/mobile/collections/
Auth: Required
Response: [CollectionSerializer, ...]
```

#### Создать коллекцию
```
POST /api/mobile/collections/
Auth: Required
Body:
{
  "name": "Интересные статьи",
  "description": "Описание",
  "is_public": false
}
```

#### Обновить коллекцию
```
PUT/PATCH /api/mobile/collections/{id}/
Auth: Required (только владелец)
```

#### Удалить коллекцию
```
DELETE /api/mobile/collections/{id}/
Auth: Required (только владелец)
```

---

### 👤 Пользователи

#### Статистика пользователя
```
GET /api/mobile/users/{id}/stats/
Response:
{
  "posts_count": 10,
  "comments_count": 25,
  "likes_received": 150,
  "followers_count": 50,
  "following_count": 30
}
```

#### Достижения пользователя
```
GET /api/mobile/users/{id}/achievements/
Response: [UserAchievementSerializer, ...]
```

#### Посты пользователя
```
GET /api/mobile/users/{id}/posts/
Response: Paginated [PostListSerializer, ...]
```

#### Избранные посты (только свой профиль)
```
GET /api/mobile/users/{id}/favorites/
Auth: Required
Response: Paginated [PostListSerializer, ...]
```

---

### 📸 Загрузка медиа

#### Загрузка изображения
```
POST /api/mobile/media/upload_image/
Auth: Required
Content-Type: multipart/form-data
Body:
  - image: <file>

Response:
{
  "url": "/media/uploads/image.jpg",
  "filename": "uploads/image.jpg"
}
```

---

## Коды ошибок

| Код | Описание |
|-----|----------|
| 400 | Bad Request - неверный запрос |
| 401 | Unauthorized - отсутствует авторизация |
| 403 | Forbidden - доступ запрещен |
| 404 | Not Found - ресурс не найден |
| 500 | Internal Server Error - ошибка сервера |

## Форматы ошибок
```json
{
  "field_name": ["Ошибка 1", "Ошибка 2"]
}

// или
{
  "error": "Описание ошибки"
}
```
