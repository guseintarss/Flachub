# 🚀 Руководство по развертыванию PageGlow

## Содержание

1. [Docker Compose (Рекомендуется)](#docker-compose)
2. [Развертывание на VPS](#vps)
3. [SSL/HTTPS](#ssl)
4. [Резервные копии](#резервные-копии)
5. [Мониторинг](#мониторинг)

---

## Docker Compose

### Требования

- Docker >= 20.10
- Docker Compose >= 1.29
- 2+ GB RAM
- 10+ GB свободного места

### Шаг 1: Подготовка сервера

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y docker.io docker-compose

# Добавить текущего пользователя в группу docker (опционально)
sudo usermod -aG docker $USER

# Перезагрузиться или выполнить:
newgrp docker

# Проверить установку
docker --version
docker-compose --version
```

### Шаг 2: Клонирование проекта

```bash
cd /opt  # или другая директория
git clone https://github.com/guseintarss/PageGlow3.0.git
cd PageGlow3.0
```

### Шаг 3: Конфигурация

```bash
# Копировать и отредактировать .env
cp .env.example .env
nano .env

# Обязательные параметры:
DEBUG=False
SECRET_KEY=your-very-secret-key-change-this
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
DATABASE_PASSWORD=your-strong-db-password

# Email (SMTP)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Шаг 4: Первый запуск

```bash
# Скачать образы и запустить контейнеры
docker-compose up -d

# Проверить статус
docker-compose ps

# Ожидайте ~30 секунд для инициализации БД
sleep 30

# Создать суперпользователя
docker-compose exec pageglow python manage.py createsuperuser

# Проверить логи
docker-compose logs -f pageglow
```

### Шаг 5: Проверка

```bash
# Проверить здоровье приложения
curl http://localhost/health/

# Ожидаемый ответ:
# {"status":"healthy","database":"ok","cache":"ok"}

# Проверить админ-панель
# Откройте в браузере: http://your-domain.com/admin
```

### Управление

```bash
# Просмотр логов
docker-compose logs -f pageglow     # Django logs
docker-compose logs -f nginx        # Nginx logs
docker-compose logs -f postgres     # Database logs

# Остановка
docker-compose down

# Перезагрузка
docker-compose restart pageglow

# Обновление (pull latest)
git pull
docker-compose build --no-cache
docker-compose up -d

# Удаление всего (включая БД!)
docker-compose down -v
```

---

## VPS (Вручную на Ubuntu/Debian)

### Требования

- Ubuntu 20.04+
- 2+ GB RAM
- 20+ GB SSD

### Шаг 1: Установка зависимостей

```bash
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y \
    python3.11 \
    python3-pip \
    python3-venv \
    postgresql \
    postgresql-contrib \
    nginx \
    git \
    curl \
    wget \
    supervisor
```

### Шаг 2: Конфигурация PostgreSQL

```bash
# Переключиться на пользователя postgres
sudo -u postgres psql

# В psql:
CREATE DATABASE pageglow_db;
CREATE USER pageglow_user WITH PASSWORD 'strong_password';
ALTER ROLE pageglow_user SET client_encoding TO 'utf8';
ALTER ROLE pageglow_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE pageglow_user SET default_transaction_deferrable TO on;
ALTER ROLE pageglow_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE pageglow_db TO pageglow_user;
\q
```

### Шаг 3: Клонирование и настройка

```bash
cd /home/youruser
git clone https://github.com/guseintarss/PageGlow3.0.git
cd PageGlow3.0/PageGlow

# Виртуальное окружение
python3.11 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install --upgrade pip
pip install -r requirements.txt

# Создать .env
cat > .env << 'EOF'
DEBUG=False
SECRET_KEY=your-very-secret-key
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DATABASE_HOST=localhost
DATABASE_NAME=pageglow_db
DATABASE_USERNAME=pageglow_user
DATABASE_PASSWORD=strong_password
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EOF

# Права доступа
chmod 600 .env
```

### Шаг 4: Django Подготовка

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### Шаг 5: Gunicorn

```bash
# Тестовый запуск
gunicorn --config gunicorn_config.py PageGlow.wsgi:application

# Systemd сервис
sudo tee /etc/systemd/system/pageglow.service > /dev/null << EOF
[Unit]
Description=PageGlow Gunicorn Service
After=network.target postgresql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/home/youruser/PageGlow3.0/PageGlow
Environment="PATH=/home/youruser/PageGlow3.0/PageGlow/venv/bin"
EnvironmentFile=/home/youruser/PageGlow3.0/PageGlow/.env
ExecStart=/home/youruser/PageGlow3.0/PageGlow/venv/bin/gunicorn \
    --workers 4 \
    --worker-class sync \
    --bind unix:/run/gunicorn.sock \
    --access-logfile - \
    --error-logfile - \
    PageGlow.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

# Активировать сервис
sudo systemctl daemon-reload
sudo systemctl start pageglow
sudo systemctl enable pageglow
sudo systemctl status pageglow
```

### Шаг 6: Nginx

```bash
# Создать конфиг
sudo tee /etc/nginx/sites-available/pageglow > /dev/null << 'EOF'
upstream pageglow_app {
    server unix:/run/gunicorn.sock;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    client_max_body_size 75M;

    location /static/ {
        alias /home/youruser/PageGlow3.0/PageGlow/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias /home/youruser/PageGlow3.0/PageGlow/media/;
    }

    location / {
        proxy_pass http://pageglow_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Активировать конфиг
sudo ln -s /etc/nginx/sites-available/pageglow /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Проверить конфиг
sudo nginx -t

# Перезагрузить
sudo systemctl restart nginx
```

### Шаг 7: Логирование

```bash
# Создать директорию логов
mkdir -p /var/log/pageglow
sudo chown www-data:www-data /var/log/pageglow

# Logrotate
sudo tee /etc/logrotate.d/pageglow > /dev/null << EOF
/var/log/pageglow/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload pageglow > /dev/null 2>&1 || true
    endscript
}
EOF
```

---

## SSL (HTTPS)

### Вариант 1: Let's Encrypt с Certbot (Рекомендуется)

```bash
# Установка
sudo apt-get install -y certbot python3-certbot-nginx

# Получить сертификат
sudo certbot certonly --nginx -d your-domain.com -d www.your-domain.com

# Обновить Nginx конфиг
sudo tee /etc/nginx/sites-available/pageglow > /dev/null << 'EOF'
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    client_max_body_size 75M;

    location /static/ {
        alias /home/youruser/PageGlow3.0/PageGlow/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias /home/youruser/PageGlow3.0/PageGlow/media/;
    }

    location / {
        proxy_pass http://pageglow_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Перезагрузить Nginx
sudo systemctl restart nginx

# Автоматическое обновление
sudo certbot renew --dry-run  # Тест
sudo certbot renew  # Реальное обновление
```

### Вариант 2: Docker + Let's Encrypt

```bash
# Использовать docker-certbot
docker run -it --rm -v /etc/letsencrypt:/etc/letsencrypt \
    certbot/certbot certonly --standalone \
    -d your-domain.com -d www.your-domain.com

# Скопировать сертификаты в проект
mkdir -p nginx/ssl
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem

# Обновить compose.yml volumes для Nginx
```

---

## Резервные копии

### Автоматическая ежедневная резервная копия БД

```bash
# Скрипт резервной копии
mkdir -p /home/youruser/backups

cat > /home/youruser/backup_db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/youruser/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/pageglow_db_$TIMESTAMP.sql"

# Для Docker
docker-compose exec -T postgres pg_dump -U postgres pageglow_db > "$BACKUP_FILE"

# Для VPS
# sudo -u postgres pg_dump pageglow_db > "$BACKUP_FILE"

# Сжатие
gzip "$BACKUP_FILE"

# Удалить старые копии (старше 30 дней)
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +30 -delete

echo "Backup created: ${BACKUP_FILE}.gz"
EOF

chmod +x /home/youruser/backup_db.sh

# Добавить в cron (ежедневно в 2:00)
crontab -e

# Добавить строку:
0 2 * * * /home/youruser/backup_db.sh
```

### Восстановление из резервной копии

```bash
# Docker
gunzip < backups/pageglow_db_20240305_020000.sql.gz | \
  docker-compose exec -T postgres psql -U postgres pageglow_db

# VPS
gunzip < backups/pageglow_db_20240305_020000.sql.gz | \
  sudo -u postgres psql pageglow_db
```

---

## Мониторинг

### Healthcheck и Alerts

```bash
# Простой скрипт мониторинга
cat > /home/youruser/check_health.sh << 'EOF'
#!/bin/bash

DOMAIN="your-domain.com"
EMAIL="admin@your-domain.com"

# Проверка здоровья
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://$DOMAIN/health/)

if [ "$HTTP_CODE" != "200" ]; then
    echo "Application health check failed!" | \
    mail -s "🚨 PageGlow Alert: Service Down" "$EMAIL"
    
    # Попытаться перезагрузить
    systemctl restart pageglow
fi
EOF

chmod +x /home/youruser/check_health.sh

# Добавить в cron (каждые 5 минут)
*/5 * * * * /home/youruser/check_health.sh
```

### Просмотр логов

```bash
# Docker
docker-compose logs -f --tail=100 pageglow
docker-compose logs -f --tail=100 nginx

# VPS
sudo journalctl -u pageglow -f
sudo tail -f /var/log/nginx/error.log
```

### Мониторинг ресурсов

```bash
# Docker
docker stats pageglow-app

# VPS - используйте htop
sudo htop

# Проверить использование диска
df -h
du -sh /home/youruser/PageGlow3.0

# Проверить использование БД
docker-compose exec postgres du -sh /var/lib/postgresql/data
```

---

## Troubleshooting

### Приложение не стартует

```bash
# Docker
docker-compose logs pageglow | grep ERROR

# VPS
sudo journalctl -u pageglow -n 50
```

### Проблемы с БД

```bash
# Docker - проверить подключение
docker-compose exec pageglow python manage.py dbshell

# VPS
sudo -u postgres psql -d pageglow_db -c "SELECT 1;"
```

### Статика не загружается

```bash
# Docker
docker-compose exec pageglow python manage.py collectstatic --noinput
docker-compose restart nginx

# VPS
python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

### 502 Bad Gateway

```bash
# Проверить Gunicorn
sudo systemctl status pageglow
sudo systemctl restart pageglow

# Проверить сокет
ls -la /run/gunicorn.sock

# Проверить Nginx логи
sudo tail -f /var/log/nginx/error.log
```

---

## Обновления

### Обновление приложения

```bash
# Docker
git pull
docker-compose build --no-cache
docker-compose down
docker-compose up -d

# VPS
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart pageglow
```

---

**Созданно: March 5, 2026**
