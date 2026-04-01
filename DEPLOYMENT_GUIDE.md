# 🚀 PageGlow 3.0 — Полное руководство по деплою

## Содержание

1. [Требования](#1-требования)
2. [Быстрый старт (3 команды)](#2-быстрый-старт)
3. [Пошаговый деплой](#3-пошаговый-деплой)
4. [Настройка .env](#4-настройка-env)
5. [SSL / HTTPS](#5-ssl--https)
6. [Управление через Makefile](#6-управление-через-makefile)
7. [Резервное копирование](#7-резервное-копирование)
8. [Обновление приложения](#8-обновление-приложения)
9. [Мониторинг и логи](#9-мониторинг-и-логи)
10. [Troubleshooting](#10-troubleshooting)
11. [Безопасность](#11-безопасность)

---

## 1. Требования

### Минимальные
| Ресурс | Значение |
|--------|----------|
| CPU | 2 ядра |
| RAM | 2 GB |
| Disk | 20 GB SSD |
| OS | Ubuntu 20.04+ / Debian 11+ |

### Рекомендуемые
| Ресурс | Значение |
|--------|----------|
| CPU | 4 ядра |
| RAM | 4 GB |
| Disk | 40 GB SSD |
| OS | Ubuntu 22.04 LTS |

### Установка Docker

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker
```

Проверка:
```bash
docker --version        # 20.10+
docker compose version  # 2.0+
```

---

## 2. Быстрый старт

```bash
git clone https://github.com/guseintarss/PageGlow3.0.git
cd PageGlow3.0
make up
```

`make up` автоматически:
- создаст `.env` с уникальным `SECRET_KEY`
- создаст все директории
- запустит все сервисы
- проверит health endpoint
- предложит применить миграции

Приложение будет доступно на `http://localhost`

---

## 3. Пошаговый деплой

### Шаг 1: Подготовка сервера

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl wget nano htop
sudo mkdir -p /opt/pageglow
sudo chown $USER:$USER /opt/pageglow
cd /opt/pageglow
```

### Шаг 2: Клонирование

```bash
git clone https://github.com/guseintarss/PageGlow3.0.git .
```

### Шаг 3: Настройка .env

```bash
cp .env.example .env
nano .env
```

Обязательно укажите:
- `SECRET_KEY` — генерируется автоматически при `make up`
- `DATABASE_PASSWORD` — надёжный пароль для БД
- `ALLOWED_HOSTS` — ваш домен
- `CSRF_TRUSTED_ORIGINS` — `https://ваш-домен.com`

### Шаг 4: Запуск

```bash
make up
```

### Шаг 5: Создание администратора

```bash
make createsuperuser
```

### Шаг 6: Проверка

```bash
make health
```

Ожидаемый ответ:
```json
{
    "status": "ok",
    "version": "3.0",
    "database": "ok"
}
```

---

## 4. Настройка .env

### Критически важные параметры

```bash
# Django
DEBUG=False
SECRET_KEY=<сгенерированный-ключ>
ALLOWED_HOSTS=ваш-домен.com,www.ваш-домен.com

# База данных
DATABASE_PASSWORD=<надёжный-пароль-мин-16-символов>

# Email (для регистрации и уведомлений)
EMAIL_HOST_USER=ваш-email@gmail.com
EMAIL_HOST_PASSWORD=<app-password-не-обычный-пароль>

# CSRF (обязательно с https://)
CSRF_TRUSTED_ORIGINS=https://ваш-домен.com,https://www.ваш-домен.com

# Домен для SEO мета-тегов
META_SITE_DOMAIN=ваш-домен.com
```

### Генерация SECRET_KEY

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Параметры Gunicorn

```bash
# Формула воркеров: (CPU * 2) + 1
# Для 2 CPU: 5 воркеров
GUNICORN_WORKERS=4
GUNICORN_WORKER_CLASS=gevent
GUNICORN_MAX_REQUESTS=1000
```

---

## 5. SSL / HTTPS

> **Важно:** По умолчанию приложение работает на HTTP (порт 80). HTTPS включается после получения сертификатов.

### Шаг 1: Получение сертификата

```bash
# Укажите ваш домен
make ssl-cert DOMAIN=ваш-домен.com
```

Certbot создаст файлы в `nginx/ssl/`.

### Шаг 2: Включение HTTPS

```bash
make ssl-enable DOMAIN=ваш-домен.com
```

Это заменит `nginx/pageglow.conf` на SSL-версию и перезапустит nginx.

### Шаг 3: Проверка

```bash
curl -I https://ваш-домен.com
```

### Автообновление сертификатов

Certbot работает как фоновый сервис в Docker и автоматически обновляет сертификаты каждые 12 часов.

Проверка:
```bash
docker compose logs certbot
```

### Откат на HTTP

Если что-то пошло не так:
```bash
git checkout nginx/pageglow.conf
docker compose restart nginx
```

---

## 6. Управление через Makefile

Все команды: `make help`

### Основные

| Команда | Описание |
|---------|----------|
| `make up` | Первый запуск / деплой |
| `make down` | Остановка всех сервисов |
| `make restart` | Перезапуск |
| `make ps` | Статус контейнеров |

### База данных

| Команда | Описание |
|---------|----------|
| `make migrate` | Применить миграции |
| `make makemigrations` | Создать миграции |
| `make dbshell` | Подключение к PostgreSQL |
| `make backup` | Бэкап БД + медиа |
| `make restore BACKUP_FILE=path` | Восстановление |

### Логи

| Команда | Описание |
|---------|----------|
| `make logs` | Все логи |
| `make logs-app` | Логи Django |
| `make logs-nginx` | Логи nginx |
| `make logs-db` | Логи PostgreSQL |

### Консоль

| Команда | Описание |
|---------|----------|
| `make shell` | Django shell |
| `make bash` | Bash в контейнере |
| `make createsuperuser` | Создать админа |

### Обновление

| Команда | Описание |
|---------|----------|
| `make update` | Pull + rebuild + restart |
| `make update-force` | Полная пересборка с нуля |
| `make clean-build` | Очистка образов и пересборка |

### SSL

| Команда | Описание |
|---------|----------|
| `make ssl-cert DOMAIN=x.com` | Получить сертификат |
| `make ssl-enable DOMAIN=x.com` | Включить HTTPS |
| `make ssl-renew` | Обновить сертификаты |

---

## 7. Резервное копирование

### Ручной бэкап

```bash
make backup
```

Создаёт:
- `backups/db_YYYYMMDD_HHMMSS.sql.gz` — дамп БД
- `backups/media_YYYYMMDD_HHMMSS.tar.gz` — медиа файлы

### Автоматический бэкап (cron)

```bash
# Ежедневно в 3:00
(crontab -l 2>/dev/null; echo "0 3 * * * cd /opt/pageglow && ./backup.sh") | crontab -
```

### Настройка хранения

```bash
# Хранить 30 дней (по умолчанию)
BACKUP_RETENTION_DAYS=30 ./backup.sh

# Хранить 7 дней
BACKUP_RETENTION_DAYS=7 ./backup.sh
```

### Восстановление

```bash
# БД
make restore BACKUP_FILE=backups/db_20260402_030000.sql.gz

# Медиа
tar -xzf backups/media_20260402_030000.tar.gz -C ./PageGlow/
```

---

## 8. Обновление приложения

### Штатное обновление

```bash
make update
```

Это выполнит:
1. `git pull` — обновление кода
2. `docker compose build` — пересборка образа
3. `docker compose up -d` — перезапуск
4. Проверка health endpoint

### Принудительное обновление

```bash
make update-force
```

Полная пересборка с миграциями и сборкой статики.

### Откат

```bash
# Вернуться к предыдущему коммиту
git reset --hard HEAD~1
make update-force
```

---

## 9. Мониторинг и логи

### Health check

```bash
make health
```

### Ресурсы контейнеров

```bash
docker stats
```

### Логи ошибок

```bash
# Django ошибки
docker compose logs pageglow | grep -i error

# Nginx ошибки
docker compose logs nginx | grep -i error

# 500-е ошибки
docker compose logs nginx | grep " 500 "
```

### Размер БД

```bash
docker compose exec postgres psql -U postgres -d pageglow_db -c \
  "SELECT pg_size_pretty(pg_database_size('pageglow_db'));"
```

---

## 10. Troubleshooting

### Контейнер не запускается

```bash
# Логи
docker compose logs pageglow | tail -50

# Проверка .env
docker compose config

# Пересборка
make clean-build
```

### 502 Bad Gateway

```bash
# Проверка что Django запущен
docker compose ps pageglow

# Проверка health
curl http://localhost/health/

# Перезапуск
docker compose restart nginx pageglow
```

### Ошибка подключения к БД

```bash
# Проверка PostgreSQL
docker compose exec postgres pg_isready

# Логи БД
docker compose logs postgres

# Проверка .env
grep DATABASE .env
```

### Проблемы со статикой

```bash
make clean-static
docker compose restart nginx
```

### Полный сброс

```bash
# ВНИМАНИЕ: удалит все данные!
make clean
make up
```

### Порты заняты

```bash
# Проверка
sudo lsof -i :80
sudo lsof -i :443
sudo lsof -i :5432

# Остановка conflicting сервисов
sudo systemctl stop apache2  # если есть
sudo systemctl stop nginx    # если есть
```

---

## 11. Безопасность

### Firewall (UFW)

```bash
sudo apt install -y ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable
sudo ufw status
```

### Fail2Ban

```bash
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### Проверка .env

```bash
# .env НЕ должен быть в git
git ls-files .env  # должно быть пусто

# Права на .env
chmod 600 .env
```

### Docker security

- Приложение работает от пользователя `django` (не root)
- Multi-stage build — минимальный образ
- `.dockerignore` исключает `.env`, `venv`, `.git`

---

## Архитектура сервисов

```
┌─────────────┐
│   Internet   │
└──────┬───────┘
       │
┌──────▼───────┐
│    Nginx     │  :80, :443
│  (reverse    │
│   proxy)     │
└──────┬───────┘
       │
┌──────▼───────┐
│   Gunicorn   │  :8000
│   (Django)   │
└──┬───────┬───┘
   │       │
┌──▼──┐ ┌──▼────┐
│ PG  │ │ Redis │
│ :5432│ │ :6379 │
└─────┘ └───────┘
```

| Сервис | Контейнер | Порт | Назначение |
|--------|-----------|------|------------|
| Nginx | `pageglow-nginx` | 80, 443 | Reverse proxy, SSL, статика |
| Django | `pageglow-app` | 8000 | Приложение |
| PostgreSQL | `pageglow-db` | 5432 | База данных |
| Redis | `pageglow-redis` | 6379 | Кэш, WebSocket |
| Certbot | `pageglow-certbot` | — | SSL автообновление |
| Adminer | `pageglow-adminer` | 8080 | UI для БД (dev only) |

---

**Последнее обновление:** Апрель 2026
**Версия:** 3.0
