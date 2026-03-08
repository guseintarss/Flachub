# 🚀 Инструкции по развёртыванию PageGlow 3.0.1

**Дата:** 8 марта 2026  
**Версия:** 3.0.1  
**Статус:** Production Ready

---

## ⚡ Быстрый старт (5 минут)

### 1. Установите зависимости

```bash
cd PageGlow
pip install -r requirements.txt
```

### 2. Примените миграции БД

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Создайте суперпользователя (администратор)

```bash
python manage.py createsuperuser
```

Следуйте подсказкам:
```
Username: admin
Email: admin@example.com
Password: ••••••••
```

### 4. Запустите сервер разработки

```bash
python manage.py runserver
```

Сайт будет доступен по адресу: **http://localhost:8000**

### 5. Откройте админку

Перейдите на: **http://localhost:8000/admin**

Используйте учетные данные администратора

---

## 📝 Полная пошаговая установка

### Шаг 1: Настройка окружения

#### На Windows:
```bash
# Создать виртуальное окружение
python -m venv venv
venv\Scripts\activate

# Перейти в директорию проекта
cd PageGlow3.0.1\PageGlow
```

#### На Linux/Mac:
```bash
# Создать виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Перейти в директорию проекта
cd PageGlow3.0.1/PageGlow
```

### Шаг 2: Установить зависимости

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Основные пакеты:**
- Django 6.0.2
- Django REST Framework 3.16.1
- PostgreSQL driver (psycopg2)
- Redis кэш
- Celery (опционально)

### Шаг 3: Настроить переменные окружения

Создайте файл `.env` в директории `PageGlow/`:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# База данных
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=pageglow_db
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=your-password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Кэш
CACHE_BACKEND=redis
REDIS_URL=redis://localhost:6379/0

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=465
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_SSL=True

# Домен
META_SITE_DOMAIN=yourdomain.com
```

### Шаг 4: Настроить БД PostgreSQL

#### Установить PostgreSQL:
```bash
# Windows
# Скачайте с: https://www.postgresql.org/download/windows/

# Linux (Ubuntu/Debian)
sudo apt-get install postgresql postgresql-contrib

# Mac
brew install postgresql
```

#### Создать БД:
```bash
# Войти в PostgreSQL
psql -U postgres

# Создать БД
CREATE DATABASE pageglow_db;
CREATE USER pageglow_user WITH PASSWORD 'password';
ALTER ROLE pageglow_user SET client_encoding TO 'utf8';
ALTER ROLE pageglow_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE pageglow_user SET default_transaction_deferrable TO on;
ALTER ROLE pageglow_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE pageglow_db TO pageglow_user;
\q
```

### Шаг 5: Миграции

```bash
# Создать миграции
python manage.py makemigrations

# Применить миграции
python manage.py migrate

# Собрать статические файлы
python manage.py collectstatic --noinput
```

### Шаг 6: Создать администратора

```bash
python manage.py createsuperuser
```

### Шаг 7: Загрузить тестовые данные (опционально)

```bash
python manage.py populate_skills_v2
```

### Шаг 8: Запустить сервер

```bash
# Development
python manage.py runserver

# Production (используя Gunicorn)
gunicorn PageGlow.wsgi:application --bind 0.0.0.0:8000
```

---

## 🐳 Docker развёртывание

### Использование Docker Compose:

```bash
# Запустить контейнеры
docker-compose -f compose.yml up -d

# Применить миграции
docker-compose exec web python manage.py migrate

# Создать суперпользователя
docker-compose exec web python manage.py createsuperuser

# Собрать статику
docker-compose exec web python manage.py collectstatic
```

Доступно по: **http://localhost:8000**

---

## 🌐 Развёртывание на Production (Linux)

### Используя Nginx + Gunicorn + Supervisor

#### 1. Установить необходимое ПО

```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv
sudo apt-get install -y postgresql postgresql-contrib
sudo apt-get install -y nginx
sudo apt-get install -y supervisor
sudo apt-get install -y redis-server
```

#### 2. Установить проект

```bash
git clone https://github.com/yourusername/PageGlow3.0.git
cd PageGlow3.0/PageGlow
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. Настроить Gunicorn

Создать файл `/etc/supervisor/conf.d/gunicorn.conf`:

```ini
[program:gunicorn]
directory=/var/www/PageGlow3.0/PageGlow
command=/var/www/PageGlow3.0/PageGlow/venv/bin/gunicorn \
    --workers 4 \
    --bind unix:/var/www/PageGlow3.0/PageGlow/gunicorn.sock \
    PageGlow.wsgi:application
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/gunicorn.log
```

#### 4. Настроить Nginx

Создать файл `/etc/nginx/sites-available/pageglow`:

```nginx
upstream gunicorn {
    server unix:/var/www/PageGlow3.0/PageGlow/gunicorn.sock fail_timeout=0;
}

server {
    listen 80;
    server_name pageglow.ru www.pageglow.ru;
    client_max_body_size 100M;

    location /static/ {
        alias /var/www/PageGlow3.0/PageGlow/staticfiles/;
    }

    location /media/ {
        alias /var/www/PageGlow3.0/PageGlow/media/;
    }

    location / {
        proxy_pass http://gunicorn;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 5. Запустить сервисы

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo systemctl restart nginx
```

---

## ✅ Проверка установки

### 1. Проверить доступность сайта
```bash
curl http://localhost:8000/health/
```

Ответ должен быть:
```json
{"status": "healthy", "database": "ok", "cache": "ok"}
```

### 2. Проверить админку
```
http://localhost:8000/admin/
```

### 3. Проверить API
```bash
curl http://localhost:8000/api-auth/
```

### 4. Проверить маркетплейс
```
http://localhost:8000/marketplace/
```

### 5. Проверить сообщество
```
http://localhost:8000/
```

---

## 🔍 Часто встречающиеся проблемы

### Проблема: ModuleNotFoundError

**Решение:**
```bash
pip install -r requirements.txt
```

### Проблема: PostgreSQL connection error

**Решение:**
```bash
# Проверить запущен ли PostgreSQL
psql -U postgres -d pageglow_db -c "SELECT 1"
```

### Проблема: Static files not found

**Решение:**
```bash
python manage.py collectstatic --noinput
```

### Проблема: Port 8000 already in use

**Решение:**
```bash
python manage.py runserver 8001
```

### Проблема: Permission denied for media uploads

**Решение:**
```bash
chmod -R 755 PageGlow/media/
chmod -R 755 PageGlow/cache/
chmod -R 755 PageGlow/logs/
```

---

## 📊 Мониторинг

### Логирование

**Логи Django:** `PageGlow/logs/django.log`  
**Логи Gunicorn:** `/var/log/gunicorn.log` (production)  
**Логи Nginx:** `/var/log/nginx/` (production)

### Проверить логи

```bash
# Django логи
tail -f PageGlow/logs/django.log

# Gunicorn логи
tail -f /var/log/gunicorn.log

# Ошибки
grep ERROR PageGlow/logs/django.log
```

---

## 🔒 Security Checklist

Перед production развёртыванием:

- [ ] Установить `DEBUG=False`
- [ ] Использовать сильный `SECRET_KEY`
- [ ] Настроить `ALLOWED_HOSTS`
- [ ] Использовать HTTPS (SSL certificates)
- [ ] Включить CSRF protection
- [ ] Включить XSS protection
- [ ] Настроить CORS правильно
- [ ] Включить rate limiting
- [ ] Настроить логирование
- [ ] Регулярно обновлять зависимости
- [ ] Создать резервные копии БД
- [ ] Настроить мониторинг

---

## 📞 Поддержка

Если вы столкнулись с проблемой:

1. **Проверить логи:**
   ```bash
   tail -f PageGlow/logs/django.log
   ```

2. **Проверить статус сервиса:**
   ```bash
   systemctl status gunicorn  # Linux
   supervisorctl status       # Linux
   ```

3. **Перезагрузить сервис:**
   ```bash
   systemctl restart gunicorn  # Linux
   supervisorctl restart all   # Linux
   ```

4. **Контактировать поддержку:**
   - Email: support@pageglow.ru
   - Телефон: +7 (999) 999-99-99

---

## 🎉 Готово!

Ваш PageGlow 3.0.1 установлен и готов к использованию!

Начните с:
1. Создания аккаунта
2. Публикации первого проекта
3. Поиска фрилансеров или работы

**Успехов в развитии платформы!** 🚀

---

**Версия документации:** 1.0.0  
**Дата обновления:** 8 марта 2026  
**Статус:** ✅ Актуально
