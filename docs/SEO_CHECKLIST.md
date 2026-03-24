# 🚀 SEO Шпаргалка PageGlow

> Краткое руководство по использованию SEO-функций платформы

---

## 📋 Быстрый чеклист публикации статьи

### Перед публикацией

- [ ] **Заголовок H1** содержит ключевое слово
- [ ] **Meta Title** 50-60 символов
- [ ] **Meta Description** 150-160 символов  
- [ ] **URL** короткий и понятный (транслит)
- [ ] **Изображения** с alt-текстами
- [ ] **Теги** 3-5 штук
- [ ] **Категория** выбрана правильно

### После публикации

- [ ] Проверить отображение в [Google Rich Results](https://search.google.com/test/rich-results)
- [ ] Проверить [Schema Validator](https://validator.schema.org/)
- [ ] Поделиться в соцсетях (проверить OG превью)

---

## 🔍 URL для проверки SEO

| Ресурс | URL |
|--------|-----|
| **Robots.txt** | https://pageglow.ru/robots.txt |
| **Sitemap.xml** | https://pageglow.ru/sitemap.xml |
| **Google Search Console** | https://search.google.com/search-console |
| **Яндекс.Вебмастер** | https://webmaster.yandex.ru |
| **Rich Results Test** | https://search.google.com/test/rich-results |
| **Mobile-Friendly Test** | https://search.google.com/test/mobile-friendly |

---

## 📊 Формулы заголовков

### Title (50-60 символов)

```
[Ключевой запрос] + [УТП/Детали] + [Бренд]

Примеры:
✅ "Как изучить Python в 2026: Полное руководство | PageGlow"
✅ "Django Tutorial для начинающих | PageGlow"
✅ "10 ошибок начинающего разработчика | PageGlow"
```

### Description (150-160 символов)

```
[Проблема] + [Решение] + [Призыв к действию]

Примеры:
✅ "Изучите Python с нуля до профессионала. Пошаговое руководство с 
примерами кода, упражнениями и проектами. Начните карьеру в IT уже сегодня!"
```

---

## 🏷️ Микроразметка (автоматическая)

### Article (для статей)

Добавляется автоматически через модель `Post`:

```python
# В models.py уже настроено:
_metadata = {
    'title': 'get_meta_title',
    'description': 'get_meta_description',
    'keywords': 'get_keywords_list',
    'image': 'get_image_full_url',
    'og_type': 'article',
    'published_time': 'get_published_time',
    'modified_time': 'get_modified_time',
    'author': 'get_author_name',
    'section': 'get_category_name',
    'tags': 'get_tags_list',
}
```

### WebSite (для сайта)

Добавлено в `base.html`:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "PageGlow",
  "url": "https://pageglow.ru",
  "potentialAction": {
    "@type": "SearchAction",
    "target": "https://pageglow.ru/search/?q={search_term_string}"
  }
}
</script>
```

---

## 📱 Social Media Preview

### Open Graph теги

Автоматически генерируются для каждой статьи:

```html
<meta property="og:type" content="article" />
<meta property="og:title" content="Заголовок статьи" />
<meta property="og:description" content="Описание статьи" />
<meta property="og:image" content="URL изображения" />
<meta property="og:url" content="URL статьи" />
```

### Twitter Card

```html
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Заголовок" />
<meta name="twitter:description" content="Описание" />
<meta name="twitter:image" content="Изображение" />
```

---

## 🎯 Ключевые слова

### Основные

- IT статьи
- Программирование обучение
- Разработка ПО
- DevOps руководства
- Системное администрирование
- Веб-разработка

### Long-tail

- "как научиться программировать с нуля"
- "руководство по Docker для начинающих"
- "лучшие практики Python разработки"
- "настройка CI/CD пайплайнов"

---

## ⚡ Технические требования

### Изображения

| Параметр | Требование |
|----------|------------|
| **Формат** | WebP, JPEG (80%), PNG для скриншотов |
| **Размер** | До 200KB |
| **OG Image** | 1200x630px |
| **Alt-текст** | Обязательно |

### Скорость загрузки

- ✅ Lazy loading включен
- ✅ Preconnect для CDN
- ✅ Кэширование Redis
- ✅ Минификация CSS/JS

---

## 📈 Мониторинг

### Еженедельно

- [ ] Проверка позиций по ключевым словам
- [ ] Анализ органического трафика
- [ ] Проверка новых ошибок в Search Console

### Ежемесячно

- [ ] Аудит старого контента
- [ ] Обновление устаревших статей
- [ ] Анализ конкурентов
- [ ] Корректировка SEO-стратегии

---

## 🔧 Команды для разработки

### Проверка SEO

```bash
# Локальная проверка
python manage.py check

# Проверка sitemap
curl http://localhost:8000/sitemap.xml

# Проверка robots.txt
curl http://localhost:8000/robots.txt
```

### Очистка кэша

```bash
# Очистка кэша Django
python manage.py clear_cache

# Перезапуск Redis
sudo systemctl restart redis
```

---

## 📞 Поддержка

- 📧 Email: support@flakhub.com
- 💬 Telegram: @pageglow
- 📚 Документация: [SEO_GUIDE.md](SEO_GUIDE.md)

---

<div align="center">

**PageGlow SEO Cheat Sheet v3.0**

Последнее обновление: Март 2026

[Наверх](#-seo-шпаргалка-pageglow)

</div>
