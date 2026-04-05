# PageGlow 3.0

Платформа для публикации статей, постов, обсуждений и социального взаимодействия. Построена на Django 6 с Docker-инфраструктурой, WebSocket-поддержкой и системой репутации.

## Содержание

- [Возможности](#возможности)
- [Стек технологий](#стек-технологий)
- [Архитектура](#архитектура)
- [Быстрый старт](#быстрый-старт)
- [Конфигурация](#конфигурация)
- [Команды Makefile](#команды-makefile)
- [Деплой](#деплой)
- [SSL/HTTPS](#sslhttps)
- [Тестирование](#тестирование)
- [Структура проекта](#структура-проекта)
- [Система репутации](#система-репутации)
- [Контроль доступа](#контроль-доступа)

---

## Возможности

- **Контент**: посты, статьи, новости, идеи с CKEditor 5
- **Обсуждения**: Q&A-темы с комментариями и ответами
- **Социальные функции**: лайки, подписки, уведомления, закладки и коллекции
- **Система репутации**: уровни, бейджи, достижения, логи репутации
- **Комментарии**: древовидные комментарии с лайками
- **SEO**: мета-теги (Open Graph), RSS-ленты, sitemap
- **Realtime**: WebSocket через Django Channels (уведомления в реальном времени)
- **Аутентификация**: Django sessions + JWT (Djoser) + Social Auth (Google и др.)
- **Кэширование**: Redis + template fragment caching

---

## Стек технологий

| Компонент | Технология |
|-----------|------------|
| Backend | Django 6, Django REST Framework 3.16 |
| База данных | PostgreSQL |
| Кэш | Redis 7 |
| Веб-сервер | Nginx (reverse proxy) |
| WSGI-сервер | Gunicorn (gevent workers) |
| WebSocket | Channels + Daphne |
| Аутентификация | Djoser + JWT + Social Auth |
| Контейнеризация | Docker + Docker Compose |
| Тестирование | pytest, pytest-django, factory-boy |
| Мониторинг | Sentry SDK |

---

## Архитектура

```
                  ┌──────────┐
                  │  Nginx   │ :80 / :443
                  │ (proxy)  │
                  └────┬─────┘
                       │
               ┌───────┴───────┐
               │               │
        ┌──────▼──────┐  ┌────▼────┐
        │  Gunicorn   │  │ Static  │
        │  Django     │  │  Files  │
        │   :8000     │  └─────────┘
        └───┬───┬─────┘
            │   │
     ┌──────┘   └──────┐
     │                 │
┌────▼────┐      ┌─────▼─────┐
│PostgreSQL│      │   Redis   │
│  :5432   │      │   :6379   │
└─────────┘      └───────────┘
```

---

## Быстрый старт

### Требования

- Docker >= 20.10
- Docker Compose >= 2.0 (или docker-compose >= 1.29)
- Make (для удобства)

### Запуск

```bash
# 1. Клонировать репозиторий
git clone <repository-url>
cd PageGlow3.0

# 2. Скопировать и настроить .env
cp .env.example .env
# Отредактируйте .env (SECRET_KEY, DATABASE_PASSWORD, и т.д.)

# 3. Запустить
make up
```

Приложение будет доступно по адресу `http://localhost`.

### Создание суперпользователя

```bash
make createsuperuser
```

---

## Конфигурация

Основные переменные окружения (`.env`):

| Переменная | Описание | Пример |
|------------|----------|--------|
| `DEBUG` | Режим отладки | `False` |
| `SECRET_KEY` | Секретный ключ Django | (авто-генерация) |
| `ALLOWED_HOSTS` | Разрешённые хосты | `localhost,your-domain.com` |
| `DATABASE_HOST` | Хост БД | `postgres` |
| `DATABASE_NAME` | Имя БД | `pageglow_db` |
| `DATABASE_USERNAME` | Пользователь БД | `postgres` |
| `DATABASE_PASSWORD` | Пароль БД | `strong-password` |
| `EMAIL_HOST_USER` | SMTP пользователь | `you@gmail.com` |
| `EMAIL_HOST_PASSWORD` | SMTP пароль | `app-password` |
| `REDIS_URL` | URL Redis | `redis://redis:6379/0` |
| `GUNICORN_WORKERS` | Кол-во воркеров Gunicorn | `4` |
| `SENTRY_DSN` | DSN Sentry (опционально) | |

---

## Команды Makefile

### Основные

| Команда | Описание |
|---------|----------|
| `make help` | Показать все команды |
| `make up` | Запуск всех сервисов |
| `make dev` | Запуск в режиме разработки (с Adminer) |
| `make prod` | Запуск в production |
| `make down` | Остановка сервисов |
| `make restart` | Перезапуск сервисов |
| `make ps` | Статус контейнеров |

### База данных

| Команда | Описание |
|---------|----------|
| `make migrate` | Применить миграции |
| `make makemigrations` | Создать миграции |
| `make dbshell` | Подключиться к PostgreSQL |
| `make backup` | Бэкап БД и медиа |
| `make restore BACKUP_FILE=file.sql.gz` | Восстановить из бэкапа |

### Логи и отладка

| Команда | Описание |
|---------|----------|
| `make logs` | Все логи |
| `make logs-app` | Логи Django |
| `make logs-nginx` | Логи Nginx |
| `make bash` | Bash в контейнере приложения |
| `make shell` | Django shell |
| `make health` | Проверка здоровья приложения |

### Тесты

| Команда | Описание |
|---------|----------|
| `make test` | Запустить тесты |
| `make test-coverage` | Тесты с покрытием |

### Очистка и обновление

| Команда | Описание |
|---------|----------|
| `make clean` | Очистка контейнеров и volumes |
| `make clean-build` | Пересборка образов без кэша |
| `make update` | Обновление с rebuild |
| `make update-force` | Полное обновление (pull + rebuild) |

---

## Деплой

Скрипт `deploy.sh` обеспечивает zero-downtime deployment с health checks:

```bash
./deploy.sh
```

Что происходит:
1. Проверка Docker и Docker Compose
2. Создание `.env` (если не существует) с авто-генерацией SECRET_KEY
3. Создание необходимых директорий
4. Graceful restart (параллельный запуск нового контейнера)
5. Health check ожидание (до 120 сек)
6. Проверка миграций

---

## SSL/HTTPS

### Получение сертификата

```bash
make ssl-cert DOMAIN=your-domain.com
```

### Включение HTTPS

```bash
make ssl-enable DOMAIN=your-domain.com
```

### Обновление сертификатов

```bash
make ssl-renew
```

Certbot автоматически обновляет сертификаты каждые 12 часов.

---

## Тестирование

```bash
# Запуск всех тестов
make test

# Тесты с покрытием
make test-coverage

# Запуск внутри контейнера
docker compose exec pageglow pytest
```

Тестовый стек: pytest, pytest-django, pytest-cov, pytest-xdist, factory-boy, Faker.

---

## Структура проекта

```
PageGlow3.0/
├── compose.yml              # Docker Compose конфигурация
├── deploy.sh                # Скрипт деплоя
├── backup.sh                # Скрипт бэкапа
├── Makefile                 # Команды управления
├── .env.example             # Шаблон окружения
├── nginx/
│   ├── pageglow.conf        # Nginx конфигурация
│   ├── ssl/                 # SSL сертификаты
│   └── certbot/             # Certbot данные
├── PageGlow/
│   ├── manage.py
│   ├── PageGlow/            # Настройки проекта
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── main/                # Основное приложение
│   │   ├── models.py        # Post, Comment, Discussion, Bookmark, Collection...
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── consumers.py     # WebSocket consumers
│   │   ├── feeds.py         # RSS ленты
│   │   └── templates/
│   ├── users/               # Приложение пользователей
│   │   ├── models.py        # User, UserLevel, UserReputationLog, Rule
│   │   ├── views.py
│   │   ├── api_views.py
│   │   ├── serializers.py
│   │   ├── reputation_utils.py
│   │   └── templates/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── gunicorn_config.py
└── backups/                 # Бэкапы БД
```

---

## Система репутации

PageGlow включает систему репутации, которая мотивирует пользователей к активному участию:

### Начисление репутации

| Действие | Репутация |
|----------|-----------|
| Публикация поста | + |
| Лайк поста (автору) | + |
| Создание комментария | + |
| Лайк комментария (автору) | + |
| Создание обсуждения | + |
| Лучший ответ | + |
| Подписка на автора | + |
| Нарушение правил | - |

### Уровни пользователей

Уровни определяются на основе накопленной репутации и дают привилегии:
- Создание тегов
- Расширенное редактирование постов
- Модерация комментариев
- Повышенный дневной лимит загрузок

### Достижения (бейджи)

Автоматическая выдача бейджей при достижении определённых целей.

---

## Контроль доступа

### Web-уровень (страницы)
- `LoginRequiredMixin` для CBV
- `@login_required` для FBV
- Фильтрация по владельцу при удалении (`get_queryset`)

### API-уровень (DRF)
- По умолчанию: `IsAuthenticated`
- Админ-ресурсы: `IsAdminUser`
- Аутентификация: JWT (Djoser) + Session

---


