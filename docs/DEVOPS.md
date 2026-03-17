# 🛠 DevOps в PageGlow

## ✅ Что реализовано

- ✅ **Sentry** - мониторинг ошибок
- ✅ **Health Check** - проверка здоровья системы
- ✅ **Backup БД** - резервное копирование
- ✅ **Логирование** - централизованные логи
- ✅ **CI/CD** - GitHub Actions

## 📁 Измененные файлы

### Backend

**requirements.txt:**
- `sentry-sdk==2.20.0` - Sentry SDK
- `django-dbbackup==4.2.0` - Backup утилита

**PageGlow/settings.py:**
- Интеграция Sentry
- Настройки dbbackup
- Логирование в файл

**main/management/commands/backup_db.py:**
- Команда `backup_db` для бэкапа БД

## 🔧 Настройка

### 1. Sentry (мониторинг ошибок)

**Регистрация:**
1. Зарегистрируйтесь на [sentry.io](https://sentry.io)
2. Создайте новый проект (Django)
3. Скопируйте DSN

**Настройка .env:**
```env
SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx
SENTRY_ENVIRONMENT=production
SENTRY_RELEASE=1.0.0
```

**Без Sentry (development):**
```env
SENTRY_DSN=
```

### 2. Health Check

**URL:** `/health/`

**Проверяет:**
- ✅ База данных
- ✅ Кэш (Redis)

**Ответ (успех):**
```json
{
  "status": "healthy",
  "database": "ok",
  "cache": "ok"
}
```

**Ответ (ошибка):**
```json
{
  "status": "unhealthy",
  "error": "Connection refused"
}
```

### 3. Backup Базы Данных

**Команда:**
```bash
python manage.py backup_db
```

**С очисткой старых:**
```bash
python manage.py backup_db --cleanup
```

**Расположение бэкапов:**
```
PageGlow/backups/
├── db_backup_20260316_120000.sql
├── db_backup_20260316_130000.sql
└── ...
```

**Настройки:**
- Хранится: 7 последних бэкапов
- Формат: SQL dump
- Автоочистка: с флагом `--cleanup`

### 4. Логирование

**Файлы логов:**
```
PageGlow/logs/
├── django.log
└── ...
```

**Уровни:**
- INFO - общая информация
- ERROR - ошибки Django

**Формат:**
```
levelnameasctime module process thread message
```

## 🚀 Использование

### Sentry

**Отправка ошибки:**
```python
import sentry_sdk

try:
    risky_operation()
except Exception as e:
    sentry_sdk.capture_exception(e)
```

**Добавление контекста:**
```python
sentry_sdk.set_user({"id": user.id, "email": user.email})
sentry_sdk.set_tag("module", "payments")
```

### Backup

**Cron (Linux):**
```bash
# Ежедневный бэкап в 3:00
0 3 * * * cd /path/to/PageGlow && python manage.py backup_db --cleanup
```

**Task Scheduler (Windows):**
```powershell
# Создать задачу в Task Scheduler
$action = New-ScheduledTaskAction -Execute "python" `
  -Argument "manage.py backup_db --cleanup" `
  -WorkingDirectory "C:\path\to\PageGlow\PageGlow"

$trigger = New-ScheduledTaskTrigger -Daily -At 3am

Register-ScheduledTask -TaskName "PageGlow Backup" `
  -Action $action -Trigger $trigger
```

### Health Check

**Docker/Kubernetes:**
```yaml
livenessProbe:
  httpGet:
    path: /health/
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
```

**Monitoring:**
```bash
# Проверка статуса
curl http://localhost:8000/health/

# В production
curl https://www.pageglow.com/health/
```

## 📊 Мониторинг

### Sentry Dashboard

**Метрики:**
- Количество ошибок
- Производительность (traces)
- Профилирование

**Оповещения:**
- Email при новых ошибках
- Slack интеграция
- Webhook

### Логи

**Просмотр:**
```bash
# Последние 100 строк
tail -f PageGlow/logs/django.log

# Поиск ошибок
grep ERROR PageGlow/logs/django.log
```

**Анализ:**
```bash
# Количество ошибок по модулям
grep ERROR PageGlow/logs/django.log | cut -d' ' -f3 | sort | uniq -c
```

## 🔒 Безопасность

### .env (не коммитить!)

```env
# Sentry
SENTRY_DSN=https://secret@ingest.sentry.io/123
SENTRY_ENVIRONMENT=production

# Database
DATABASE_PASSWORD=secret

# Secret Key
SECRET_KEY=django-insecure-secret-key
```

### Backup Security

- Шифрование бэкапов (опционально)
- Хранение в отдельном месте
- Ограниченный доступ

## 📈 Производительность

### Sentry Performance

**Traces Sample Rate:**
- `0.1` = 10% транзакций
- Уменьшить для high-traffic

**Profiles Sample Rate:**
- `0.1` = 10% профилей
- Помогает найти узкие места

### Log Rotation

**Настройки:**
- Max size: 10MB
- Backup count: 10 файлов
- Encoding: UTF-8

## 🔮 Будущие улучшения

- [ ] Автоматический деплой (CI/CD)
- [ ] Мониторинг ресурсов (CPU, RAM)
- [ ] Alerting (Telegram, Slack)
- [ ] Load balancing
- [ ] CDN для статики
- [ ] Database replication

---

**Создано:** 2026-03-16  
**Статус:** ✅ Готово  
**Инструменты:** Sentry, dbbackup, logging
