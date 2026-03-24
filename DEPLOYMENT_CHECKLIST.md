# 🚀 DEPLOYMENT CHECKLIST - PageGlow 3.0

## 📋 Предварительная проверка

### 1. Конфигурация и безопасность

- [ ] **DEBUG = False** в `.env`
- [ ] **SECRET_KEY** изменён на уникальный (минимум 50 символов)
- [ ] **ALLOWED_HOSTS** настроен на ваш домен
- [ ] **DATABASE_PASSWORD** установлен на сложный пароль
- [ ] **EMAIL_HOST_PASSWORD** использует app-specific password
- [ ] Файл `.env` добавлен в `.gitignore`
- [ ] Файл `.env` имеет права `chmod 600 .env`

### 2. База данных

- [ ] PostgreSQL настроен и доступен
- [ ] Миграции применены: `python manage.py migrate`
- [ ] Суперпользователь создан: `python manage.py createsuperuser`
- [ ] Резервное копирование настроено (ежедневно)

### 3. Статические файлы

- [ ] `python manage.py collectstatic --noinput` выполнено
- [ ] Nginx настроен для раздачи статики
- [ ] MEDIA_ROOT имеет правильные права доступа

### 4. Веб-сервер

- [ ] Gunicorn/Daphne настроен и запущен
- [ ] Nginx настроен как reverse proxy
- [ ] SSL/HTTPS настроен (Let's Encrypt)
- [ ] HTTP → HTTPS редирект работает

### 5. Мониторинг

- [ ] Healthcheck endpoint доступен: `/health/`
- [ ] Логирование настроено
- [ ] Оповещения об ошибках настроены

---

## 🔧 Быстрый старт (Docker)

```bash
# 1. Клонировать проект
cd /opt
git clone https://github.com/guseintarss/PageGlow3.0.git
cd PageGlow3.0

# 2. Настроить .env
cp .env.example .env
nano .env

# 3. Запустить
docker-compose up -d

# 4. Создать суперпользователя
docker-compose exec pageglow python manage.py createsuperuser

# 5. Проверить
curl http://localhost/health/
```

---

## 🔧 Быстрый старт (VPS)

```bash
# 1. Установка зависимостей
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv postgresql nginx git

# 2. База данных
sudo -u postgres psql -c "CREATE DATABASE pageglow_db;"
sudo -u postgres psql -c "CREATE USER pageglow_user WITH PASSWORD 'strong_pass';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE pageglow_db TO pageglow_user;"

# 3. Проект
cd /home/youruser
git clone https://github.com/guseintarss/PageGlow3.0.git
cd PageGlow3.0/PageGlow

# 4. Виртуальное окружение
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Настройка
cp ../.env.example .env
nano .env

# 6. Django
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput

# 7. Gunicorn сервис
sudo tee /etc/systemd/system/pageglow.service > /dev/null << EOF
[Unit]
Description=PageGlow Service
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
    --bind unix:/run/gunicorn.sock \
    PageGlow.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl start pageglow
sudo systemctl enable pageglow

# 8. Nginx
sudo tee /etc/nginx/sites-available/pageglow > /dev/null << 'EOF'
server {
    listen 80;
    server_name your-domain.com;
    
    location /static/ {
        alias /home/youruser/PageGlow3.0/PageGlow/staticfiles/;
    }
    
    location /media/ {
        alias /home/youruser/PageGlow3.0/PageGlow/media/;
    }
    
    location / {
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/pageglow /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔒 Security Checklist

- [ ] DEBUG = False
- [ ] SECRET_KEY >= 50 символов
- [ ] ALLOWED_HOSTS настроен
- [ ] HTTPS включен
- [ ] HSTS заголовок установлен
- [ ] CSRF защита включена
- [ ] XSS защита включена
- [ ] Пароли хешируются (PBKDF2/Argon2)
- [ ] Админка защищена (не на /admin/)
- [ ] Rate limiting настроен
- [ ] Брандмауэр настроен (UFW)
- [ ] Fail2ban установлен
- [ ] Автоматические обновления безопасности включены

---

## 📊 Performance Checklist

- [ ] Кэширование включено (Redis/Memcached)
- [ ] Gunicorn workers >= 4
- [ ] Nginx gzip включен
- [ ] Статика раздаётся через Nginx
- [ ] Медиа файлы оптимизированы
- [ ] Database индексы настроены
- [ ] Query оптимизированы (нет N+1)
- [ ] CDN для статики (опционально)

---

## 📝 Команды для проверки

```bash
# Проверка здоровья
curl https://your-domain.com/health/

# Проверка HTTPS
curl -I https://your-domain.com/

# Проверка редиректа HTTP → HTTPS
curl -I http://your-domain.com/

# Проверка статики
curl -I https://your-domain.com/static/main/css/app.css

# Проверка админки
curl -I https://your-domain.com/admin/

# Проверка логов
sudo tail -f /var/log/nginx/error.log
sudo journalctl -u pageglow -f

# Проверка использования ресурсов
htop
df -h
free -h
```

---

## 🆘 Troubleshooting

### 502 Bad Gateway
```bash
sudo systemctl status pageglow
sudo systemctl restart pageglow
ls -la /run/gunicorn.sock
```

### Статика 404
```bash
python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

### База данных не доступна
```bash
sudo systemctl status postgresql
sudo -u postgres psql -d pageglow_db -c "SELECT 1;"
```

### Приложение не стартует
```bash
# Docker
docker-compose logs pageglow | tail -50

# VPS
sudo journalctl -u pageglow -n 50
```

---

## 📞 Контакты для поддержки

- **Email:** support@pageglow.com
- **GitHub:** https://github.com/guseintarss/PageGlow3.0/issues
- **Документация:** https://github.com/guseintarss/PageGlow3.0/wiki

---

**Последнее обновление:** March 24, 2026
**Версия:** 3.0
