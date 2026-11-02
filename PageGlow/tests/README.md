# Тестирование в PageGlow

Тесты написаны на **pytest** + **pytest-django**. Проверяются модели, API и
SPA-маршрутизация.

## Запуск

```bash
cd PageGlow
source venv/bin/activate

# Все тесты
pytest

# Только API / маршруты / модели
pytest tests/test_api.py tests/test_views.py tests/test_models.py

# Без отчёта о покрытии (быстрее)
pytest --no-cov

# Пересоздать тестовую БД, если мешает кэш
pytest --create-db
```

Для проверки SPA-маршрутов желательно собрать фронтенд:

```bash
cd ../frontend
npm run build
```

Если сборки нет, Django отдаёт запасной `PageGlow/templates/index.html`,
поэтому тесты маршрутизации всё равно проходят.

## Структура

```
PageGlow/
├── conftest.py          # общие фикстуры
├── pytest.ini           # настройки pytest
└── tests/
    ├── test_models.py   # модели, slug, репутация
    ├── test_views.py    # SPA-маршруты, health, URL моделей
    └── test_api.py      # публикация, права, комментарии, CSRF
```

## Основные фикстуры

### Пользователи

- `user` — обычный пользователь;
- `another_user` — второй пользователь;
- `admin_user` — суперпользователь;
- `user_factory` / `create_user` — фабрики пользователей.

### Клиенты

- `client` — Django test client;
- `logged_in_client` — клиент с `force_login`;
- `api_client` — DRF APIClient;
- `authenticated_api_client` — APIClient с `force_authenticate` (без JWT и
  без CSRF-проверки).

### Контент

- `category`, `tag`;
- `post` — опубликованная статья;
- `draft_post` — черновик;
- `published_posts` — набор статей;
- `comment`, `subscription`, `rule`;
- `create_post` — фабрика статей.

## Примеры

```python
def test_published_post_has_url(post):
    assert post.get_absolute_url() == f'/post/{post.slug}/'


def test_create_post(authenticated_api_client, category):
    response = authenticated_api_client.post('/api/mobile/posts/', {
        'title': 'API Post',
        'content': '<p>Текст</p>',
        'cat': category.id,
        'is_published': '1',
    })
    assert response.status_code == 201
```

CSRF для анонимных запросов проверяется отдельно: сначала получите токен
через `GET /api/mobile/me/`, затем передайте его в заголовке `X-CSRFToken`.

## Покрытие

```bash
pytest --cov-report=term-missing --cov-report=html
```

Отчёт будет в `htmlcov/index.html`.
