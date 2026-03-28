# 🚀 PageGlow 3.0 - Полное руководство по деплою

## Содержание

1. [Требования](#требования)
2. [Быстрый старт с Docker Compose](#быстрый-старт)
3. [Настройка окружения](#настройка-окружения)
4. [SSL/HTTPS настройка](#sslhttps)
5. [Резервное копирование](#резервное-копирование)
6. [Мониторинг и логи](#мониторинг)
7. [Troubleshooting](#troubleshooting)

---

## Требования

### Минимальные
- **CPU:** 2 ядра
- **RAM:** 2 GB
- **Disk:** 20 GB SSD
- **OS:** Ubuntu 20.04+ / Debian 11+

### Рекомендуемые
- **CPU:** 4 ядра
- **RAM:** 4 GB
- **Disk:** 40 GB SSD
- **OS:** Ubuntu 22.04 LTS

### Необходимое ПО
```bash
# Docker и Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Проверка версий
docker --version        # 20.10+
docker compose version  # 2.0+
```

---

## Быстрый старт

### Шаг 1: Подготовка сервера

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка необходимых пакетов
sudo apt install -y git curl wget nano htop

# Создание директории для проекта
sudo mkdir -p /opt/pageglow
sudo chown $USER:$USER /opt/pageglow
cd /opt/pageglow
```

### Шаг 2: Клонирование проекта

```bash
git clone https://github.com/guseintarss/PageGlow3.0.git .
# или скопируйте файлы проекта в эту директорию
```

### Шаг 3: Настройка .env файла

```bash
# Копирование примера
cp .env.example .env

# Генерация секретного ключа
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Редактирование .env
nano .env
```

### Шаг 4: Первый запуск

```bash
# Запуск всех сервисов
docker compose up -d

# Проверка статуса
docker compose ps

# Ожидание инициализации (30-60 секунд)
sleep 45

# Создание суперпользователя
docker compose exec pageglow python manage.py createsuperuser

# Проверка логов
docker compose logs -f pageglow
```

### Шаг 5: Проверка работы

```bash
# Health check
curl http://localhost/health/

# Проверка nginx
curl -I http://localhost/

# Проверка приложения
curl http://localhost:8000/admin/
```

---

## Настройка окружения

### .env файл - обязательные параметры

```bash
# ===== DJANGO SETTINGS =====
DEBUG=False
SECRET_KEY=ваш-секретный-ключ-минимум-50-символов
ALLOWED_HOSTS=ваш-домен.com,www.ваш-домен.com

# ===== DATABASE =====
DATABASE_NAME=pageglow_db
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=очень-сложный-пароль-от-бд

# ===== EMAIL (для уведомлений) =====
EMAIL_HOST_USER=ваш-email@gmail.com
EMAIL_HOST_PASSWORD=пароль-приложения
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=465

# ===== GUNICORN =====
GUNICORN_WORKERS=4
GUNICORN_WORKER_CLASS=gevent
GUNICORN_BIND=0.0.0.0:8000

# ===== SECURITY =====
CSRF_TRUSTED_ORIGINS=https://ваш-домен.com
```

### Генерация SECRET_KEY

```bash
# Python
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# OpenSSL
openssl rand -base64 64

# /dev/urandom
head -c 50 /dev/urandom | base64
```

---

## SSL/HTTPS

### Вариант 1: Certbot (Let's Encrypt)

```bash
# Создание директории для сертификатов
mkdir -p nginx/certbot

# Запуск certbot
docker run --rm -it \
  -v $(pwd)/nginx/certbot:/etc/letsencrypt \
  -v $(pwd)/nginx/ssl:/var/www/certbot \
  certbot/certbot certonly --webroot \
  --webroot-path=/var/www/certbot \
  --email ваш-email@example.com \
  --agree-tos --no-eff-email \
  -d ваш-домен.com -d www.ваш-домен.com
```

### Настройка nginx для HTTPS

1. Откройте `nginx/pageglow.conf`
2. Раскомментируйте HTTPS блок
3. Включите редирект на HTTPS

```nginx
# В HTTP блоке:
return 301 https://$server_name$request_uri;

# В HTTPS блоке раскомментируйте:
ssl_certificate /etc/nginx/ssl/fullchain.pem;
ssl_certificate_key /etc/nginx/ssl/privkey.pem;
```

### Автоматическое обновление сертификатов

```bash
# Скрипт обновления
cat > renew-cert.sh << 'EOF'
#!/bin/bash
docker run --rm -it \
  -v $(pwd)/nginx/certbot:/etc/letsencrypt \
  -v $(pwd)/nginx/ssl:/var/www/certbot \
  certbot/certbot renew
docker compose restart nginx
EOF

chmod +x renew-cert.sh

# Добавить в cron (ежемесячно)
crontab -e
0 0 1 * * /opt/pageglow/renew-cert.sh
```

---

## Резервное копирование

### Автоматический бэкап БД

```bash
# Скрипт бэкапа
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/pageglow/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/pageglow_$TIMESTAMP.sql.gz"

mkdir -p $BACKUP_DIR

# Бэкап базы данных
docker compose exec -T postgres pg_dump -U postgres $DATABASE_NAME | gzip > $BACKUP_FILE

# Бэкап медиа файлов
tar -czf $BACKUP_DIR/media_$TIMESTAMP.tar.gz ./PageGlow/media/

# Удаление старых бэкапов (старше 30 дней)
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup created: $BACKUP_FILE"
EOF

chmod +x backup.sh

# Добавить в cron (ежедневно в 3:00)
crontab -e
0 3 * * * /opt/pageglow/backup.sh
```

### Восстановление из бэкапа

```bash
# Восстановление БД
gunzip < backups/pageglow_20240328_030000.sql.gz | \
  docker compose exec -T postgres psql -U postgres pageglow_db

# Восстановление медиа
tar -xzf backups/media_20240328_030000.tar.gz -C ./PageGlow/
```

---

## Мониторинг

### Просмотр логов

```bash
# Все логи
docker compose logs -f

# Логи приложения
docker compose logs -f pageglow

# Логи nginx
docker compose logs -f nginx
tail -f nginx_logs/error.log

# Логи базы данных
docker compose logs -f postgres
```

### Health check

```bash
# Проверка статуса
curl http://localhost/health/

# Ожидаемый ответ:
# {"status":"healthy","database":"ok","cache":"ok"}
```

### Мониторинг ресурсов

```bash
# Использование ресурсов контейнерами
docker stats

# Проверка дискового пространства
df -h
du -sh /opt/pageglow/*

# Проверка размера БД
docker compose exec postgres du -sh /var/lib/postgresql/data
```

### Логирование ошибок

```bash
# Ошибки Django
docker compose logs pageglow | grep ERROR

# Ошибки nginx
docker compose logs nginx | grep error

# Ошибки БД
docker compose logs postgres | grep ERROR
```

---

## Обновление приложения

### Плановое обновление

```bash
# Остановка сервисов
docker compose down

# Обновление кода
git pull

# Пересборка образов
docker compose build --no-cache

# Запуск
docker compose up -d

# Проверка
docker compose ps
docker compose logs -f pageglow
```

### Миграции

```bash
# Применение миграций
docker compose exec pageglow python manage.py migrate

# Сбор статики
docker compose exec pageglow python manage.py collectstatic --noinput

# Перезапуск приложения
docker compose restart pageglow
```

---

## Troubleshooting

### Приложение не запускается

```bash
# Проверка логов
docker compose logs pageglow | tail -100

# Проверка подключения к БД
docker compose exec pageglow python manage.py dbshell

# Пересоздание контейнера
docker compose rm -f pageglow
docker compose up -d pageglow
```

### Ошибка 502 Bad Gateway

```bash
# Проверка nginx
docker compose logs nginx | grep error

# Проверка gunicorn
docker compose logs pageglow | grep -i error

# Перезапуск сервисов
docker compose restart nginx pageglow

# Проверка сокетов
docker compose exec pageglow ls -la /run/
```

### Проблемы со статикой

```bash
# Пересбор статики
docker compose exec pageglow python manage.py collectstatic --noinput --clear

# Проверка прав доступа
docker compose exec pageglow ls -la /app/staticfiles/

# Перезапуск nginx
docker compose restart nginx
```

### Проблемы с БД

```bash
# Проверка здоровья БД
docker compose exec postgres pg_isready

# Проверка подключений
docker compose exec postgres psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

# Ваккуумирование
docker compose exec postgres psql -U postgres -c "VACUUM ANALYZE;"
```

### Сброс и чистый запуск

```bash
# Полная остановка
docker compose down

# Удаление volumes (ВНИМАНИЕ: удалит все данные!)
docker compose down -v

# Чистый запуск
docker compose up -d
docker compose exec pageglow python manage.py migrate
docker compose exec pageglow python manage.py createsuperuser
```

---

## Производительность

### Оптимизация Gunicorn

```bash
# Количество воркеров (формула: CPU * 2 + 1)
# Для 4 CPU: 4 * 2 + 1 = 9 воркеров

# В .env:
GUNICORN_WORKERS=9
GUNICORN_WORKER_CLASS=gevent
GUNICORN_MAX_REQUESTS=1000
```

### Оптимизация nginx

```nginx
# В nginx/pageglow.conf добавить:
worker_processes auto;
worker_rlimit_nofile 65535;

events {
    worker_connections 4096;
    use epoll;
    multi_accept on;
}

http {
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    keepalive_requests 100;
}
```

### Оптимизация PostgreSQL

```bash
# В postgresql.conf (создать volume mount)
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
max_connections = 100
```

---

## Безопасность

### Firewall (UFW)

```bash
# Установка
sudo apt install ufw

# Настройка правил
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable

# Проверка
sudo ufw status
```

### Fail2Ban

```bash
# Установка
sudo apt install fail2ban

# Создание конфига
cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[nginx-http-auth]
enabled = true
port = http,https
filter = nginx-http-auth
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
port = http,https
filter = nginx-limit-req
logpath = /var/log/nginx/error.log
EOF

sudo systemctl restart fail2ban
```

### Docker Security

```bash
# Запуск от непривилегированного пользователя
# Уже настроено в Dockerfile

# Сканирование уязвимостей
docker scout cve pageglow:latest

# Проверка конфигураций
docker compose config --quiet
```

---

**Последнее обновление:** 28 марта 2026  
**Версия:** 3.0
