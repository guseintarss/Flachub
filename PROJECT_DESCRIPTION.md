# 🌟 PageGlow 3.0

> **Современная платформа для IT-специалистов: делитесь знаниями, находите возможности и развивайтесь вместе с нами.**

[![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)](https://github.com/guseintarss/PageGlow3.0)
[![Django](https://img.shields.io/badge/Django-6.0-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.14-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

---

## 📖 О проекте

**PageGlow** — это полнофункциональная платформа для публикации и обсуждения IT-статей, руководств и новостей. Платформа объединяет разработчиков, системных администраторов, DevOps-инженеров и других IT-специалистов для обмена опытом и знаниями.

### 🎯 Цели проекта

- 📚 **Обмен знаниями** — публикация качественных статей и руководств
- 👥 **Сообщество** — объединение IT-специалистов разных уровней
- 💡 **Обучение** — доступ к актуальным материалам и лучшим практикам
- 🔍 **Поиск информации** — удобная система поиска и категоризации

---

## ✨ Ключевые возможности

### 📝 Публикации

| Функция | Описание |
|---------|----------|
| **Rich-редактор** | CKEditor 5 с поддержкой форматирования кода |
| **Категории и теги** | Удобная организация контента |
| **Черновики** | Сохранение статей перед публикацией |
| **Редактирование** | Изменение опубликованных материалов |
| **Статистика** | Просмотры, лайки, комментарии |

### 👤 Профиль пользователя

- 📊 **Личный кабинет** — управление статьями и настройками
- 🔖 **Закладки** — сохранение понравившихся статей
- ⭐ **Избранное** — коллекция лучших материалов
- 📬 **Подписки** — отслеживание авторов
- 🏆 **Достижения** — система бейджей и наград

### 💬 Сообщество

- 💬 **Комментарии** — обсуждение статей с древовидной структурой
- ❤️ **Лайки** — оценка качества материалов
- 🔔 **Уведомления** — real-time оповещения (AJAX Polling)
- 📢 **Обсуждения** — отдельный раздел для дискуссий
- 📧 **Рассылка** — подписка на новые материалы

### 🔍 Поиск и навигация

- 🔎 **Полнотекстовый поиск** — по заголовкам и содержанию
- 📂 **Категории** — иерархическая структура
- 🏷️ **Теги** — гибкая система тегирования
- 📈 **Популярное** — топ статей за период
- 📰 **Лента подписок** — статьи авторов, на которых вы подписаны

---

## 🛠️ Технологический стек

### Backend

| Технология | Версия | Назначение |
|------------|--------|------------|
| **Python** | 3.14 | Язык программирования |
| **Django** | 6.0 | Web-фреймворк |
| **Django REST Framework** | 3.16 | API |
| **PostgreSQL** | 15+ | База данных |
| **Redis** | 7+ | Кэш и очереди |
| **Channels** | 4.2 | WebSocket поддержка |
| **BeautifulSoup4** | 4.14 | Парсинг HTML |
| **Pillow** | 12.1 | Обработка изображений |

### Frontend

| Технология | Назначение |
|------------|------------|
| **HTML5/CSS3** | Базовая разметка и стили |
| **JavaScript (Vanilla)** | Интерактивность |
| **Bootstrap 5.3** | Адаптивный дизайн |
| **Font Awesome 6.4** | Иконки |
| **CKEditor 5** | WYSIWYG редактор |

### DevOps

| Технология | Назначение |
|------------|------------|
| **Docker** | Контейнеризация |
| **Docker Compose** | Оркестрация контейнеров |
| **Nginx** | Reverse proxy и статика |
| **Gunicorn** | WSGI сервер |
| **Daphne** | ASGI сервер (WebSocket) |
| **GitHub Actions** | CI/CD |

---

## 📁 Структура проекта

```
PageGlow3.0/
├── PageGlow/                 # Основное Django приложение
│   ├── main/                # Приложение: статьи, комментарии, теги
│   ├── users/               # Приложение: пользователи, профили
│   ├── PageGlow/            # Настройки проекта
│   │   ├── settings.py      # Конфигурация Django
│   │   ├── urls.py          # Маршруты
│   │   ├── asgi.py          # ASGI конфигурация
│   │   └── wsgi.py          # WSGI конфигурация
│   ├── templates/           # Общие шаблоны
│   ├── static/              # Статические файлы
│   └── media/               # Медиа файлы
├── nginx/                   # Конфигурация Nginx
├── agents/                  # AI агенты (планируется)
├── docs/                    # Документация
├── .github/workflows/       # CI/CD пайплайны
├── compose.yml              # Docker Compose конфигурация
├── deploy.sh                # Скрипт деплоя
├── backup.sh                # Скрипт резервного копирования
├── .env.example             # Шаблон переменных окружения
├── requirements.txt         # Python зависимости
└── README.md                # Этот файл
```

---

## 🚀 Быстрый старт

### Требования

- Python 3.14+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (опционально)

### Установка (локальная разработка)

```bash
# Клонировать репозиторий
git clone https://github.com/guseintarss/PageGlow3.0.git
cd PageGlow3.0

# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установить зависимости
pip install -r PageGlow/requirements.txt

# Настроить .env
cp .env.example .env
nano .env  # Отредактируйте настройки

# Применить миграции
python PageGlow/manage.py migrate

# Создать суперпользователя
python PageGlow/manage.py createsuperuser

# Запустить сервер разработки
python PageGlow/manage.py runserver
```

### Установка (Docker)

```bash
# Клонировать репозиторий
git clone https://github.com/guseintarss/PageGlow3.0.git
cd PageGlow3.0

# Настроить .env
cp .env.example .env
nano .env

# Запустить контейнеры
docker-compose up -d

# Создать суперпользователя
docker-compose exec pageglow python manage.py createsuperuser
```

---

## 📚 Документация

| Документ | Описание |
|----------|----------|
| [DEPLOYMENT.md](DEPLOYMENT.md) | Полное руководство по развертыванию |
| [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) | Чеклист для продакшена |
| [TESTING_GUIDE.md](TESTING_GUIDE.md) | Руководство по тестированию |
| [CHANGELOG.md](CHANGELOG.md) | История изменений |

---

## 🔧 Конфигурация

### Переменные окружения

```bash
# Django
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=your-domain.com

# Database
DATABASE_NAME=pageglow_db
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=your-password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Email
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Cache
REDIS_URL=redis://localhost:6379/0
```

---

## 🧪 Тестирование

```bash
# Запустить все тесты
pytest

# Запустить с покрытием
pytest --cov=PageGlow --cov-report=html

# Запустить конкретный тест
pytest tests/test_models.py -v
```

---

## 🤝 Вклад в проект

Мы приветствуем вклад в развитие PageGlow! 

### Как внести вклад

1. Fork репозиторий
2. Создайте ветку (`git checkout -b feature/AmazingFeature`)
3. Закоммитьте изменения (`git commit -m 'Add some AmazingFeature'`)
4. Отправьте в репозиторий (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

### Правила кода

- Следуйте [PEP 8](https://pep8.org/)
- Пишите осмысленные комментарии
- Добавляйте тесты для новых функций
- Обновляйте документацию

---

## 📊 Статистика проекта

- 📦 **Статей опубликовано:** 1000+
- 👥 **Пользователей:** 500+
- 💬 **Комментариев:** 5000+
- 🏷️ **Тегов:** 200+
- 📂 **Категорий:** 15+

---

## 🛡️ Безопасность

PageGlow следует лучшим практикам безопасности:

- ✅ HTTPS/SSL шифрование
- ✅ CSRF защита
- ✅ XSS защита
- ✅ SQL Injection защита
- ✅ Хеширование паролей (PBKDF2)
- ✅ Rate limiting
- ✅ Валидация данных

### Сообщение об уязвимостях

Если вы обнаружили уязвимость, пожалуйста, сообщите на **pageglow3@gmail.com**

---

## 📝 Лицензия

Этот проект распространяется под лицензией **MIT**. См. файл [LICENSE](LICENSE) для деталей.

---

## 👨‍💻 Авторы

- **Temirlan** - *Основной разработчик* - [@guseintarss](https://github.com/guseintarss)

Смотрите полный список [участников](../../graphs/contributors) для деталей.

---

## 🙏 Благодарности

- [Django Team](https://www.djangoproject.com/) - за превосходный фреймворк
- [CKEditor](https://ckeditor.com/) - за отличный редактор
- [Bootstrap](https://getbootstrap.com/) - за UI фреймворк
- [Font Awesome](https://fontawesome.com/) - за иконки
- Всем контрибьюторам и пользователям проекта

---

## 📞 Контакты

- **Email:** pageglow3@gmail.com
- **GitHub:** https://github.com/guseintarss/PageGlow3.0
- **Сайт:** https://pageglow.ru
- **Telegram:** [@pageglow](https://t.me/pageglow)

---

## 🗺️ Roadmap

### v3.1 (Q2 2026)
- [ ] AI-ассистент для написания статей
- [ ] Экспорт статей в PDF/Markdown
- [ ] Мобильное приложение (PWA)
- [ ] Темная тема по умолчанию

### v3.2 (Q3 2026)
- [ ] Интеграция с GitHub/GitLab
- [ ] Система репутации пользователей
- [ ] Платные подписки
- [ ] Аналитика для авторов

### v4.0 (Q4 2026)
- [ ] Мультиязычность
- [ ] GraphQL API
- [ ] Микросервисная архитектура
- [ ] Kubernetes поддержка

---

<div align="center">

**Сделано с ❤️ для IT-сообщества**

[Наверх](#pageglow-30) • [Документация](#-документация) • [Деплой](#-быстрый-старт)

</div>
