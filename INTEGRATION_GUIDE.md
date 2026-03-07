# 📚 Руководство по интеграции PageGlow Marketplace

## 🎯 Введение

Данное руководство описывает интеграцию маркетплейса с основным приложением PageGlow и реализацию всех новых функций.

---

## 📋 Содержание

1. [Подготовка окружения](#подготовка-окружения)
2. [Миграции БД](#миграции-бд)
3. [Стилизация](#стилизация)
4. [Индикатор прогресса чтения](#индикатор-прогресса-чтения)
5. [Подписки пользователей](#подписки-пользователей)
6. [API Endpoints](#api-endpoints)
7. [Сигналы и автоматизация](#сигналы-и-автоматизация)
8. [Тестирование](#тестирование)

---

## 🚀 Подготовка окружения

### Установка зависимостей

```bash
# Убедитесь, что установлены все зависимости из requirements.txt
pip install -r requirements.txt

# Если нужно добавить новые пакеты:
pip install pillow django-rest-framework
```

### Проверка конфигурации

В файле `PageGlow/settings.py` убедитесь, что установлены:

```python
INSTALLED_APPS = [
    'marketplace.apps.MarketplaceConfig',
    'users.apps.UsersConfig',  # Убедитесь, что это первое!
    'main.apps.MainConfig',
    # ... остальные приложения
]

# Добавьте в settings.py если нет:
SITE_URL = 'http://localhost:8000'  # Или ваш адрес
```

---

## 💾 Миграции БД

### Применение миграций

```bash
# Перейдите в директорию проекта
cd PageGlow

# Примените миграции
python manage.py migrate

# Если возникают проблемы, создайте миграции вручную
python manage.py makemigrations users marketplace
python manage.py migrate
```

### Что добавляет миграция

- ✅ Поле `subscriptions` в User (ManyToMany)
- ✅ Поле `subscribers` (обратная связь)
- ✅ Временные метки `created_at`, `updated_at`
- ✅ Связь с Post для избранного

---

## 🎨 Стилизация

### Подключение CSS

В базовом шаблоне `templates/base.html` добавьте:

```html
<!-- Design System CSS -->
<link rel="stylesheet" href="{% static 'main/css/marketplace-design-system.css' %}">

<!-- Marketplace Custom Styles -->
<link rel="stylesheet" href="{% static 'main/css/marketplace-custom.css' %}">
```

### Переменные дизайна

Все переменные CSS находятся в `:root`:

```css
--color-primary: #4a90e2;           /* Основной синий */
--color-success: #4CAF50;           /* Зеленый для успеха */
--color-bg-main: #f9f9f9;           /* Фон страницы */
--color-bg-card: #ffffff;           /* Фон карточек */
--color-text-primary: #333333;      /* Основной текст */
--color-text-secondary: #666666;    /* Вторичный текст */
```

### Использование утилит

```html
<!-- Примеры использования утилит CSS -->

<!-- Карточка -->
<div class="card">
  <div class="card-header">Заголовок</div>
  <div class="card-body">Контент</div>
</div>

<!-- Кнопка -->
<button class="btn btn-primary">Действие</button>
<button class="btn btn-secondary btn-lg">Большая кнопка</button>

<!-- Badge -->
<span class="badge badge-primary">Новое</span>

<!-- Сетка -->
<div class="grid grid-3">
  <div>Колонка 1</div>
  <div>Колонка 2</div>
  <div>Колонка 3</div>
</div>
```

---

## 📊 Индикатор прогресса чтения

### Подключение скрипта

В шаблон статьи добавьте:

```html
{% load static %}

<!-- Для автоматической инициализации -->
<article data-reading-progress>
  <!-- Содержимое статьи -->
</article>

<script src="{% static 'main/js/reading-progress.js' %}"></script>
```

### Ручная инициализация

```html
<script src="{% static 'main/js/reading-progress.js' %}"></script>
<script>
  // Инициализация с опциями
  ReadingProgress.init({
    contentSelector: '.article-content',
    progressBarColor: '#4a90e2',
    completionColor: '#4CAF50',
    completionMessageDuration: 2000,
    showCompletionMessage: true,
    trackingCallback: function(progress) {
      console.log('Progress:', progress + '%');
      // Отправляйте данные на сервер если нужно
    }
  });
</script>
```

### API индикатора

```javascript
// Получить текущий прогресс (0-100)
const progress = ReadingProgress.getProgress();

// Сбросить индикатор
ReadingProgress.reset();

// Обновить конфигурацию
ReadingProgress.updateConfig({
  progressBarColor: '#ff0000'
});

// Уничтожить индикатор
ReadingProgress.destroy();
```

---

## 👥 Подписки пользователей

### Добавление в профиль

В шаблон профиля добавьте:

```html
{% include 'users/subscriptions_widget.html' with subscriptions=user.subscriptions.all subscribers=user.subscribers.all subscriptions_count=subscriptions_count subscribers_count=subscribers_count %}
```

### Получение данных в view

```python
from django.contrib.auth import get_user_model

User = get_user_model()

def user_profile(request, user_id):
    user = User.objects.get(id=user_id)
    subscriptions = user.subscriptions.all()[:6]
    subscribers = user.subscribers.all()[:6]
    
    context = {
        'user': user,
        'subscriptions': subscriptions,
        'subscribers': subscribers,
        'subscriptions_count': user.get_subscriptions_count(),
        'subscribers_count': user.get_subscribers_count(),
    }
    return render(request, 'users/profile.html', context)
```

### Методы пользователя

```python
# Получить подписки пользователя
subscriptions = user.subscriptions.all()

# Получить подписчиков пользователя
subscribers = user.subscribers.all()

# Количество подписок
count = user.get_subscriptions_count()

# Количество подписчиков
count = user.get_subscribers_count()

# Проверить подписку
is_subscribed = user.is_subscribed_to(other_user)

# Подписаться
user.subscribe_to(other_user)

# Отписаться
user.unsubscribe_from(other_user)
```

---

## 🔌 API Endpoints

### Подписки

#### Получить подписки пользователя
```bash
GET /api/subscriptions/{user_id}/subscriptions/?page=1&limit=20
```

**Ответ:**
```json
{
  "count": 15,
  "results": [
    {
      "id": 1,
      "username": "john_doe",
      "first_name": "John",
      "last_name": "Doe",
      "photo": "/media/users/avatar.jpg"
    }
  ],
  "page": 1,
  "limit": 20
}
```

#### Получить подписчиков пользователя
```bash
GET /api/subscriptions/{user_id}/subscribers/?page=1&limit=20
```

#### Подписаться на пользователя
```bash
POST /api/subscriptions/{user_id}/subscribe/

# Ответ:
{
  "message": "Вы подписались на этого пользователя",
  "subscribed": true
}
```

#### Отписаться от пользователя
```bash
POST /api/subscriptions/{user_id}/unsubscribe/

# Ответ:
{
  "message": "Вы отписались от этого пользователя",
  "subscribed": false
}
```

#### Проверить подписку
```bash
GET /api/subscriptions/{user_id}/is_subscribed/

# Ответ:
{
  "is_subscribed": true,
  "target_user_id": 1,
  "current_user_id": 2
}
```

### Статистика пользователя

#### Получить статистику
```bash
GET /api/users/{user_id}/stats/

# Ответ:
{
  "user_id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "subscriptions_count": 15,
  "subscribers_count": 25,
  "freelancer": {
    "rating": 4.8,
    "total_projects": 20,
    "total_reviews": 18,
    "is_verified": true,
    "is_available": true
  }
}
```

---

## ⚙️ Сигналы и автоматизация

### Автоматическое создание профиля маркетплейса

При регистрации нового пользователя автоматически:

1. ✅ Создается профиль в `FreelancerProfile`
2. ✅ Устанавливается рейтинг 5.0
3. ✅ Отправляется приветственное письмо
4. ✅ Синхронизируются аватар и данные

### Отправка писем

Убедитесь, что в `settings.py` настроена отправка писем:

```python
# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'noreply@pageglow.ru'
```

### Логирование сигналов

Все события логируются в консоль. Для логирования в файл:

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/signals.log',
        },
    },
    'loggers': {
        'users.signals': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

---

## 🧪 Тестирование

### Запуск тестов

```bash
# Все тесты
python manage.py test

# Тесты конкретного приложения
python manage.py test users
python manage.py test marketplace

# Тесты с verbose выводом
python manage.py test users -v 2
```

### Создание тестовых данных

```bash
# Загрузить фикстуры
python manage.py loaddata users/fixtures/test_users.json

# Или через shell
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
User = get_user_model()

# Создать тестового пользователя
user = User.objects.create_user(
    username='testuser',
    email='test@example.com',
    password='testpass123'
)

# Подписать на другого пользователя
other_user = User.objects.get(username='john_doe')
user.subscribe_to(other_user)
```

### Проверка целостности данных

```bash
# Проверить целостность БД
python manage.py check

# Проверить миграции
python manage.py showmigrations

# Проверить синтаксис кода
python manage.py runserver --check
```

---

## 🐛 Решение проблем

### Проблема: Сигналы не срабатывают

**Решение:**
1. Проверьте, что `UsersConfig` стоит первым в `INSTALLED_APPS`
2. Убедитесь, что в `users/apps.py` есть метод `ready()`
3. Перезагрузите Django сервер

### Проблема: CSS не применяется

**Решение:**
1. Запустите `python manage.py collectstatic`
2. Проверьте пути в `STATIC_URL` и `STATIC_ROOT`
3. Очистите кэш браузера (Ctrl+Shift+Delete)

### Проблема: Индикатор не отображается

**Решение:**
1. Проверьте консоль браузера (F12) на ошибки JavaScript
2. Убедитесь, что элемент контента имеет атрибут `data-reading-progress`
3. Проверьте, что скрипт загружается перед `</body>`

### Проблема: Письма не отправляются

**Решение:**
1. Проверьте настройки Email в settings.py
2. Убедитесь, что пароль приложения верный (Google требует специальный пароль)
3. Проверьте логи: `python manage.py shell` → `from django.core.mail import send_mail`

---

## 📈 Метрики производительности

### Целевые метрики

- ⚡ Время загрузки страницы: < 2 сек
- 📊 Отказы на статьях: ↓ 15%
- ⏱️ Среднее время на сайте: ↑ 20%
- 📈 Конверсия в регистрацию: ↑ 10%

### Мониторинг

```bash
# Проверить количество запросов БД
python manage.py shell
from django.test.utils import override_settings
from django.db import connection
from django.test import TestCase

# В shell:
from django.db import reset_queries
from django.conf import settings

settings.DEBUG = True
reset_queries()
# ... ваш код ...
print(len(connection.queries))  # Количество запросов
```

---

## 📚 Дополнительные ресурсы

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Django Signals](https://docs.djangoproject.com/en/stable/topics/signals/)

---

**Обновлено**: 7 марта 2026  
**Версия**: 1.0  
**Статус**: ✅ Полная интеграция
