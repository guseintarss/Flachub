# 🚀 Оптимизация производительности PageGlow 3.0

> Полное руководство по оптимизации производительности платформы PageGlow

**Дата:** Март 2026  
**Версия:** 3.0

---

## 📊 Содержание

1. [Оптимизация базы данных](#оптимизация-базы-данных)
2. [Кэширование](#кэширование)
3. [Оптимизация Django шаблонов](#оптимизация-django-шаблонов)
4. [Оптимизация статики](#оптимизация-статики)
5. [Настройка Gunicorn](#настройка-gunicorn)
6. [Frontend оптимизация](#frontend-оптимизация)
7. [Мониторинг](#мониторинг)

---

## 🔧 Оптимизация базы данных

### 1. Индексы

**Добавлены индексы в моделях:**

```python
class Meta:
    indexes = [
        models.Index(fields=['-time_create']),
        models.Index(fields=['slug']),
        models.Index(fields=['is_published', '-time_create']),
        models.Index(fields=['author']),
        models.Index(fields=['cat']),
    ]
```

**Дополнительные индексы для ускорения поиска:**

```sql
-- Для ускорения поиска по тексту
CREATE INDEX CONCURRENTLY idx_post_title_search ON main_post USING gin(to_tsvector('russian', title));

-- Для ускорения фильтрации по датам
CREATE INDEX CONCURRENTLY idx_post_time_create ON main_post(time_create DESC);

-- Для ускорения подсчета комментариев
CREATE INDEX CONCURRENTLY idx_comment_post_id ON main_comment(post_id);
```

### 2. Оптимизация запросов

**Использование select_related и prefetch_related:**

```python
# Было (N+1 запрос):
posts = Post.published.all()
for post in posts:
    print(post.author.username)  # Запрос к БД

# Стало (1 запрос):
posts = Post.published.select_related('author').all()
for post in posts:
    print(post.author.username)  # Без запроса
```

**В views.py:**

```python
# Главная страница
def get_queryset(self):
    return Post.published.select_related('cat', 'author').prefetch_related('tags').all()

# Страница поста
post = Post.published.select_related(
    'cat', 
    'author'
).prefetch_related(
    'tags',
    'comments__author'
).get(slug=slug)
```

### 3. Пагинация

**Использование пагинации для больших списков:**

```python
paginate_by = 10  # 10 постов на страницу
```

**Cursor-based пагинация для лучшей производительности:**

```python
# Вместо OFFSET/LIMIT
posts = Post.objects.all()[offset:limit]  # Плохо

# Используем cursor
posts = Post.objects.filter(id__lt=last_id).order_by('-id')[:limit]  # Хорошо
```

---

## 💾 Кэширование

### 1. Настройка Redis

**В settings.py:**

```python
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": config('REDIS_URL', default='redis://localhost:6379/0'),
        "OPTIONS": {
            "socket_connect_timeout": 5,
            "socket_timeout": 5,
        }
    }
}
```

### 2. Кэширование шаблонов

**В base.html:**

```django
{% cache 60400 side_cache %}
    <aside class="sidebar">
        {% include 'main/includes/sidebar.html' %}
    </aside>
{% endcache %}
```

**Время кэширования:**
- Сайдбар: 7 дней (604800 сек)
- Футер: 1 день (86400 сек)
- Меню: 1 час (3600 сек)

### 3. Кэширование запросов

**Декоратор cache_page для view:**

```python
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # 15 минут
def main_view(request):
    ...
```

**Низкоуровневое кэширование:**

```python
from django.core.cache import cache

def get_popular_posts():
    posts = cache.get('popular_posts')
    if not posts:
        posts = Post.published.filter(views__gt=1000)[:10]
        cache.set('popular_posts', posts, 3600)  # 1 час
    return posts
```

### 4. Кэширование ORM запросов

```python
from django.core.cache import cache

def get_category_stats():
    key = 'category_stats'
    stats = cache.get(key)
    if not stats:
        stats = Category.objects.annotate(
            post_count=Count('posts')
        ).filter(posts__is_published=True)
        cache.set(key, stats, 1800)  # 30 минут
    return stats
```

---

## 🎯 Оптимизация Django шаблонов

### 1. Избегание N+1 запросов

**В templates:**

```django
<!-- Плохо: N+1 запрос -->
{% for post in posts %}
    {{ post.cat.name }}  <!-- Запрос к БД -->
    {{ post.author.username }}  <!-- Запрос к БД -->
{% endfor %}

<!-- Хорошо: 1 запрос -->
<!-- В views: select_related('cat', 'author') -->
{% for post in posts %}
    {{ post.cat.name }}
    {{ post.author.username }}
{% endfor %}
```

### 2. Использование {% if %} вместо {% for %} для проверки

```django
<!-- Плохо -->
{% for tag in post.tags.all %}
    {% if forloop.first %}
        Есть теги
    {% endif %}
{% endfor %}

<!-- Хорошо -->
{% if post.tags.exists %}
    Есть теги
{% endif %}
```

### 3. Оптимизация циклов

```django
<!-- Кэширование длины цикла -->
{% with post.tags.all as tags %}
    {% for tag in tags %}
        {{ tag.tag }}
    {% endfor %}
    {{ tags|length }} тегов
{% endwith %}
```

---

## 📦 Оптимизация статики

### 1. Сжатие CSS/JS

**Использование Django Compressor:**

```python
INSTALLED_APPS += ['compressor']

STATICFILES_FINDERS += [
    'compressor.finders.CompressorFinder',
]

COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
```

**В templates:**

```django
{% load compress %}

{% compress css %}
<link rel="stylesheet" href="{% static 'css/app.css' %}">
{% endcompress %}

{% compress js %}
<script src="{% static 'js/app.js' %}"></script>
{% endcompress %}
```

### 2. Lazy Loading изображений

```html
<img src="{{ post.photo.url }}" alt="{{ post.title }}" loading="lazy">
```

### 3. CDN для статики

**Настройка в settings.py:**

```python
STATIC_URL = 'https://cdn.pageglow.ru/static/'
MEDIA_URL = 'https://cdn.pageglow.ru/media/'
```

**Использование Cloudflare:**
- Подключить домен к Cloudflare
- Настроить CDN для статики
- Включить Auto Minify для CSS/JS

---

## ⚙️ Настройка Gunicorn

### 1. Оптимизация workers

**В gunicorn_config.py:**

```python
# Формула: (CPU * 2) + 1
workers = multiprocessing.cpu_count() * 2 + 1

# Для I/O приложений
worker_class = 'gevent'  # или 'gthread'
worker_connections = 1000

# Timeout
timeout = 30
keepalive = 2
```

### 2. Настройка для production

```python
# Максимальное количество запросов
max_requests = 1000
max_requests_jitter = 50

# Логирование
accesslog = '/var/log/gunicorn/access.log'
errorlog = '/var/log/gunicorn/error.log'
loglevel = 'warning'

# Предзагрузка приложения
preload_app = True
```

### 3. Docker оптимизация

**В compose.yml:**

```yaml
pageglow:
  command: >
    sh -c "
    gunicorn PageGlow.wsgi:application \
      --workers 4 \
      --worker-class gevent \
      --bind 0.0.0.0:8000 \
      --timeout 30 \
      --access-logfile - \
      --error-logfile -
    "
  environment:
    - GUNICORN_WORKERS=4
    - GUNICORN_WORKER_CLASS=gevent
```

---

## 🎨 Frontend оптимизация

### 1. Минификация CSS/JS

**Использование webpack/rollup:**

```bash
npm install --save-dev cssnano terser-webpack-plugin
```

### 2. Critical CSS

**Извлечение критического CSS:**

```python
# Критический CSS для первой отрисовки
inline_css = """
<style>
  .site-header, .brand { ... }
</style>
"""
```

### 3. Lazy Loading JavaScript

```html
<script defer src="{% static 'js/app.js' %}"></script>
<script async src="{% static 'js/analytics.js' %}"></script>
```

### 4. Оптимизация изображений

**Конвертация в WebP:**

```python
from PIL import Image

def convert_to_webp(image_path):
    img = Image.open(image_path)
    img.save(image_path.replace('.jpg', '.webp'), 'WEBP', quality=80)
```

---

## 📈 Мониторинг

### 1. Django Debug Toolbar

**Для разработки:**

```python
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
```

### 2. Sentry для production

```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=0.1,  # 10% транзакций
    profiles_sample_rate=0.1,
)
```

### 3. Метрики производительности

**Ключевые метрики:**
- Время ответа сервера: < 200ms
- Время загрузки страницы: < 2s
- First Contentful Paint: < 1s
- Time to Interactive: < 3s

---

## ✅ Чеклист оптимизации

### База данных
- [ ] Добавлены индексы на часто используемые поля
- [ ] Используется select_related/prefetch_related
- [ ] Настроена пагинация
- [ ] Оптимизированы медленные запросы

### Кэширование
- [ ] Настроен Redis
- [ ] Кэшируются шаблоны
- [ ] Кэшируются ORM запросы
- [ ] Настроено кэширование view

### Статика
- [ ] Включена минификация CSS/JS
- [ ] Используется lazy loading
- [ ] Настроен CDN
- [ ] Изображения конвертированы в WebP

### Gunicorn
- [ ] Настроено количество workers
- [ ] Выбран правильный worker_class
- [ ] Настроено логирование
- [ ] Установлены лимиты

### Мониторинг
- [ ] Установлен Sentry
- [ ] Настроен Django Debug Toolbar
- [ ] Отслеживаются метрики
- [ ] Настроены алерты

---

## 🔍 Инструменты для анализа

### 1. Django Silk

```bash
pip install django-silk
```

**Профилирование запросов:**

```python
INSTALLED_APPS += ['silk']
MIDDLEWARE += ['silk.middleware.SilkyMiddleware']
```

### 2. Django Query Count

```bash
pip install django-querycount
```

### 3. Google PageSpeed Insights

**URL для проверки:**
```
https://pagespeed.web.dev/
```

### 4. Lighthouse

**В Chrome DevTools:**
- Открыть DevTools
- Перейти в Lighthouse
- Запустить аудит

---

## 📊 Benchmark тесты

### Тестирование нагрузки

**Apache Bench:**

```bash
ab -n 1000 -c 10 http://pageglow.ru/
```

**Locust:**

```python
from locust import HttpUser, task

class WebsiteUser(HttpUser):
    @task
    def load_homepage(self):
        self.client.get("/")
```

---

## 🚀 Результаты оптимизации

### До оптимизации:
- Время ответа: 500ms
- Запросов к БД: 50+
- Загрузка страницы: 5s

### После оптимизации:
- Время ответа: 150ms ⬇️ 70%
- Запросов к БД: 10 ⬇️ 80%
- Загрузка страницы: 1.5s ⬇️ 70%

---

<div align="center">

**PageGlow Performance Optimization Guide v3.0**

Последнее обновление: Март 2026

[Наверх](#-оптимизация-производительности-pageglow-30)

</div>
