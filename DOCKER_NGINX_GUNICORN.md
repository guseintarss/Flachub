# Настройка Docker, Nginx и Gunicorn

## 📋 Обзор архитектуры

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│    Nginx    │────▶│  Gunicorn   │
│  (Port 80/  │     │  (Reverse   │     │   (Django   │
│    443)     │     │   Proxy)    │     │    WSGI)    │
└─────────────┘     └─────────────┘     └─────────────┘
                           │                    │
                           │                    ▼
                           │            ┌─────────────┐
                           │            │   Django    │
                           │            │    App      │
                           │            └─────────────┘
                           │                    │
                           ▼                    ▼
                    ┌─────────────┐     ┌─────────────┐
                    │  PostgreSQL │     │    Redis    │
                    │  (Port 5432)│     │  (Port 6379)│
                    └─────────────┘     └─────────────┘
```

## 🚀 Быстрый старт

### 1. Генерация SSL сертификатов (для тестирования)

```bash
# Самоподписанные сертификаты для локальной разработки
./nginx/ssl/generate-self-signed.sh
```

### 2. Настройка переменных окружения

```bash
# Скопируйте .env.example в .env и настройте
cp .env.example .env

# Отредактируйте .env, особенно:
# - SECRET_KEY (минимум 50 символов)
# - DATABASE_PASSWORD
# - ALLOWED_HOSTS (ваш домен)
```

### 3. Запуск приложения

```bash
# Разработка (с Adminer)
docker compose --profile tools up -d

# Production
docker compose up -d
```

### 4. Проверка

```bash
# Статус сервисов
docker compose ps

# Логи
docker compose logs -f

# Health check
curl http://localhost/health/
```

## 🔧 Конфигурация

### Nginx

**Файл:** `nginx/pageglow.conf`

**Основные возможности:**
- ✅ Автоматический редирект HTTP → HTTPS
- ✅ Gzip сжатие
- ✅ Кэширование статики (30 дней)
- ✅ WebSocket поддержка
- ✅ Защита от скрытых файлов
- ✅ HSTS заголовок

**Порты:**
- `80` - HTTP (редирект на HTTPS)
- `443` - HTTPS

### Gunicorn

**Файл:** `PageGlow/gunicorn_config.py`

**Переменные окружения:**
| Переменная | По умолчанию | Описание |
|-----------|-------------|----------|
| `GUNICORN_BIND` | `0.0.0.0:8000` | Адрес и порт |
| `GUNICORN_WORKERS` | `4` | Количество воркеров |
| `GUNICORN_WORKER_CLASS` | `gevent` | Тип воркеров |
| `GUNICORN_TIMEOUT` | `120` | Таймаут запроса |
| `GUNICORN_MAX_REQUESTS` | `1000` | Перезапуск после N запросов |

**Рекомендации по воркерам:**
- Формула: `(CPU ядра × 2) + 1`
- Для `gevent`: можно больше для I/O операций

### Docker Compose

**Файл:** `compose.yml`

**Сервисы:**
| Сервис | Порт | Описание |
|-------|------|----------|
| `nginx` | 80, 443 | Reverse proxy |
| `pageglow` | 8000 (внутр.) | Django приложение |
| `postgres` | 5432 | База данных |
| `redis` | 6379 | Кэш |
| `adminer` | 8080 | Админка БД (profile: tools) |

## 📝 Полезные команды

```bash
# Просмотр логов
docker compose logs -f pageglow
docker compose logs -f nginx

# Перезапуск сервисов
docker compose restart

# Остановка
docker compose down

# Пересборка
docker compose build --no-cache

# Миграции
docker compose exec pageglow python manage.py migrate

# Сбор статики
docker compose exec pageglow python manage.py collectstatic --noinput

# Создание суперпользователя
docker compose exec pageglow python manage.py createsuperuser

# Подключение к БД
docker compose exec postgres psql -U postgres -d pageglow_db

# Health check
curl http://localhost/health/
```

## 🔒 SSL/TLS сертификаты

### Для production (Let's Encrypt)

```bash
# Получение сертификата
make ssl-cert DOMAIN=pageglow.ru

# Обновление
make ssl-renew
```

### Для разработки (самоподписанные)

```bash
./nginx/ssl/generate-self-signed.sh
```

## 🐛 Отладка

### Nginx не проксирует на Gunicorn

1. Проверьте, что Gunicorn запущен:
   ```bash
   docker compose ps pageglow
   ```

2. Проверьте логи Gunicorn:
   ```bash
   docker compose logs pageglow
   ```

3. Проверьте health endpoint напрямую:
   ```bash
   docker compose exec pageglow curl http://localhost:8000/health/
   ```

### Ошибки подключения к БД

1. Проверьте, что PostgreSQL запущен:
   ```bash
   docker compose ps postgres
   ```

2. Проверьте логи:
   ```bash
   docker compose logs postgres
   ```

3. Проверьте переменные окружения в `.env`

### Проблемы со статикой

```bash
# Пересобрать статику
docker compose exec pageglow python manage.py collectstatic --clear --noinput
docker compose restart nginx
```

## 📊 Мониторинг

### Проверка здоровья

```bash
# Nginx
curl http://localhost/health/

# Gunicorn (напрямую)
docker compose exec pageglow curl http://localhost:8000/health/
```

### Ресурсы

```bash
# Использование памяти/CPU
docker stats
```

## 🎯 Production чеклист

- [ ] Измените `SECRET_KEY` на уникальный (50+ символов)
- [ ] Установите `DEBUG=False`
- [ ] Настройте `ALLOWED_HOSTS` для вашего домена
- [ ] Используйте production SSL сертификаты (Let's Encrypt)
- [ ] Настройте бэкапы БД
- [ ] Установите надежный пароль БД
- [ ] Настройте мониторинг и логирование
- [ ] Протестируйте health endpoints

## 📚 Дополнительные ресурсы

- [Docker Compose документация](https://docs.docker.com/compose/)
- [Nginx документация](https://nginx.org/en/docs/)
- [Gunicorn документация](https://docs.gunicorn.org/)
- [Django deployment](https://docs.djangoproject.com/en/stable/howto/deployment/)
