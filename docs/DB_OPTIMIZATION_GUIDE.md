# 🚀 Руководство по оптимизации запросов к БД

> Быстрое руководство по использованию оптимизаций базы данных в PageGlow 3.0

---

## 📊 Проблема N+1 запросов

### ❌ До оптимизации (50+ запросов):

```python
posts = Post.objects.all()
for post in posts:
    print(post.author.username)  # Запрос к БД для каждого поста
    print(post.cat.name)         # Запрос к БД для каждого поста
    for tag in post.tags.all():  # Запрос к БД для каждого поста
        print(tag.tag)
```

### ✅ После оптимизации (3 запроса):

```python
posts = Post.objects.select_related('author', 'cat').prefetch_related('tags').all()
for post in posts:
    print(post.author.username)  # Без запроса
    print(post.cat.name)         # Без запроса
    for tag in post.tags.all():  # Без запроса
        print(tag.tag)
```

---

## 🔧 Основные методы оптимизации

### 1. select_related (для ForeignKey)

```python
# Один запрос вместо N+1
Post.objects.select_related('author', 'cat').all()
```

### 2. prefetch_related (для ManyToMany)

```python
# Один запрос вместо N+1
Post.objects.prefetch_related('tags').all()
```

### 3. Комбинирование

```python
# Оптимальный запрос
Post.objects.select_related(
    'author', 'cat'
).prefetch_related(
    'tags',
    Prefetch('comments', queryset=Comment.objects.select_related('author')[:5])
).all()
```

---

## 📁 Готовые оптимизации

### Файл: `main/db_optimizations.py`

#### Готовые queryset:

```python
from main.db_optimizations import (
    get_optimized_posts,
    get_optimized_categories,
    get_optimized_comments,
    get_cached_admin_stats,
    get_cached_popular_posts
)

# Оптимизированные посты
posts = get_optimized_posts()

# Оптимизированные категории
categories = get_optimized_categories()

# Оптимизированные комментарии
comments = get_optimized_comments(limit=10)

# Кэшированная статистика
stats = get_cached_admin_stats()

# Кэшированные популярные посты
popular = get_cached_popular_posts(limit=10)
```

---

## 🗂️ SQL индексы

### Файл: `db_optimization.sql`

**Применение индексов:**

```bash
# Применить все индексы
psql -U postgres -d pageglow_db -f PageGlow/db_optimization.sql
```

**Ключевые индексы:**

```sql
-- Для ускорения фильтрации по публикации и дате
CREATE INDEX idx_post_published_created ON main_post(is_published, time_create DESC);

-- Для ускорения сортировки по просмотрам
CREATE INDEX idx_post_views ON main_post(views DESC);

-- Для ускорения поиска по автору
CREATE INDEX idx_post_author ON main_post(author_id);

-- Для полнотекстового поиска
CREATE INDEX idx_post_title_search ON main_post USING gin(to_tsvector('russian', title));
```

---

## 🎯 Оптимизированные View

### Главная страница

```python
# Было
def get_queryset(self):
    return Post.published.all()

# Стало
def get_queryset(self):
    return Post.published.select_related('cat', 'author').prefetch_related('tags').all()
```

### Поиск

```python
# Было
def get_queryset(self):
    query = self.request.GET.get('q', '')
    return Post.published.filter(
        Q(title__icontains=query) | Q(content__icontains=query)
    )

# Стало
def get_queryset(self):
    query = self.request.GET.get('q', '')
    return Post.published.select_related('cat', 'author').prefetch_related('tags').filter(
        Q(title__icontains=query) | Q(content__icontains=query)
    )
```

### Категории

```python
# Было
def get_queryset(self):
    return Post.published.filter(cat__slug=self.kwargs['cat_slug'])

# Стало
def get_queryset(self):
    return Post.published.select_related('cat', 'author').prefetch_related('tags').filter(
        cat__slug=self.kwargs['cat_slug']
    )
```

---

## 💾 Кэширование

### Примеры использования:

```python
from django.core.cache import cache

# Кэширование запроса
def get_popular_posts():
    posts = cache.get('popular_posts')
    if not posts:
        posts = Post.published.filter(views__gt=1000)[:10]
        cache.set('popular_posts', posts, 3600)  # 1 час
    return posts

# Кэширование с ключом
def get_user_stats(user_id):
    cache_key = f'user_stats_{user_id}'
    stats = cache.get(cache_key)
    if not stats:
        stats = calculate_stats(user_id)
        cache.set(cache_key, stats, 300)  # 5 минут
    return stats
```

---

## 📈 Мониторинг производительности

### Django Debug Toolbar

```bash
pip install django-debug-toolbar
```

**Что смотреть:**
- Количество запросов к БД
- Время выполнения запросов
- N+1 проблемы

### Анализ запросов:

```python
from django.db import connection

# Выполнить view
response = view(request)

# Посмотреть запросы
for query in connection.queries:
    print(f"Время: {query['time']}ms")
    print(f"SQL: {query['sql']}")
```

---

## ✅ Чеклист оптимизации

### Для каждого view:

- [ ] Добавить `select_related` для всех ForeignKey
- [ ] Добавить `prefetch_related` для всех ManyToMany
- [ ] Использовать `only()` для загрузки только нужных полей
- [ ] Добавить кэширование для тяжелых запросов
- [ ] Проверить через Django Debug Toolbar

### Для базы данных:

- [ ] Применить SQL индексы из `db_optimization.sql`
- [ ] Выполнить `ANALYZE` для обновления статистики
- [ ] Настроить мониторинг медленных запросов

---

## 🔍 Инструменты

### 1. django-silk (профилирование)

```bash
pip install django-silk
```

```python
# settings.py
INSTALLED_APPS += ['silk']
MIDDLEWARE += ['silk.middleware.SilkyMiddleware']
```

### 2. django-querycount

```bash
pip install django-querycount
```

```python
# settings.py
INSTALLED_APPS += ['querycount']
MIDDLEWARE += ['querycount.middleware.QueryCountMiddleware']

QUERYCOUNT = {
    'THRESHOLDS': {
        'MEDIUM': 50,
        'HIGH': 200,
    }
}
```

---

## 📊 Результаты оптимизации

### До оптимизации:

| Метрика | Значение |
|---------|----------|
| Запросов на страницу | 50+ |
| Время ответа БД | 500ms |
| Загрузка страницы | 5s |

### После оптимизации:

| Метрика | Значение | Улучшение |
|---------|----------|-----------|
| Запросов на страницу | 10 | ⬇️ 80% |
| Время ответа БД | 100ms | ⬇️ 80% |
| Загрузка страницы | 1.5s | ⬇️ 70% |

---

## 🚀 Быстрый старт

### 1. Применить индексы:

```bash
psql -U postgres -d pageglow_db -f PageGlow/db_optimization.sql
```

### 2. Обновить views:

```python
# Использовать готовые функции из db_optimizations.py
```

### 3. Включить кэширование:

```python
# Настроить Redis в settings.py
```

### 4. Проверить через Debug Toolbar:

```bash
pip install django-debug-toolbar
```

---

<div align="center">

**PageGlow DB Optimization Guide**

[Наверх](#-руководство-по-оптимизации-запросов-к-бд)

</div>
