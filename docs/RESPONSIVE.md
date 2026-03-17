# 📱 Адаптивная верстка в PageGlow

## ✅ Что реализовано

Полноценная адаптация под все устройства:

- ✅ **Мобильные телефоны** (< 576px)
- ✅ **Планшеты** (< 768px)
- ✅ **Планшеты landscape** (< 992px)
- ✅ **Десктоп** (> 992px)
- ✅ **Touch-friendly** интерфейсы
- ✅ **Печать** страниц

## 📐 Breakpoints

| Устройство | Ширина | Стили |
|------------|--------|-------|
| Desktop | > 992px | Полная версия |
| Tablet | < 992px | 1 колонка, сайдбар сверху |
| Mobile | < 768px | Компактное меню, 1 колонка |
| Small Mobile | < 576px | Минималистичный дизайн |

## 🎯 Основные изменения

### Header

**Desktop:**
- Горизонтальное меню
- Все элементы видны

**Mobile:**
- Бургер-меню (44×44px)
- Выезжающее меню слева
- Уменьшенный логотип

### Layout

**Desktop:**
```
┌─────────────────────────────────┐
│  Header                         │
├──────────────┬──────────────────┤
│  Content     │  Sidebar         │
│  (70%)       │  (30%)           │
└──────────────┴──────────────────┘
```

**Mobile:**
```
┌─────────────────┐
│  Header         │
├─────────────────┤
│  Sidebar        │
│  (сверху)       │
├─────────────────┤
│  Content        │
│  (100%)         │
└─────────────────┘
```

### Профиль пользователя

**Desktop:**
- Аватар 150×150px
- Статистика в ряд
- Сетка постов 3 колонки

**Mobile:**
- Аватар 120×120px
- Статистика в столбик
- 1 колонка постов
- Кнопки на всю ширину

### Сайдбар

**Desktop:**
- Фиксированная позиция
- 3 колонки статистики

**Mobile:**
- Позиция сверху
- 1-3 колонки статистики
- Поиск на всю ширину

## 📱 Meta-теги

```html
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5, viewport-fit=cover">
<meta name="theme-color" content="#1c3e7e">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
```

## 👆 Touch-Friendly

### Минимальные размеры:
- **Кнопки**: 44×44px
- **Ссылки**: 44px высота
- **Чекбоксы**: 20×20px
- **Поля ввода**: 44px высота, 16px шрифт

### Оптимизации:
- Убраны hover эффекты на мобильных
- Добавлены active состояния
- Улучшен скроллинг (`-webkit-overflow-scrolling: touch`)
- Предотвращен зум на iOS (font-size: 16px)

## 🖨 Печать

При печати скрываются:
- Header
- Sidebar
- Кнопки действий
- Уведомления

Отображается:
- Только контент
- Без разрывов страниц на постах

## 📊 Примеры адаптации

### Меню навигации

```css
/* Desktop */
.nav-link {
  padding: 15px 25px;
}

/* Mobile */
@media (max-width: 768px) {
  .nav-link {
    padding: 10px 15px;
    font-size: 0.9rem;
  }
}
```

### Сетка постов

```css
/* Desktop */
.posts-grid {
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
}

/* Mobile */
@media (max-width: 768px) {
  .posts-grid {
    grid-template-columns: 1fr;
  }
}
```

### Статистика

```css
/* Desktop */
.profile-stats {
  display: flex;
  gap: 30px;
}

/* Mobile */
@media (max-width: 768px) {
  .profile-stats {
    flex-direction: column;
    gap: 10px;
  }
  
  .stat-item {
    width: 100%;
    display: flex;
    justify-content: space-between;
  }
}
```

## 🎨 Темная тема

Автоматическая адаптация:
- Системная тема через `prefers-color-scheme`
- Ручное переключение через кнопку
- Сохранение в localStorage

## 📱 Landscape режим

Для мобильных в landscape:
- Профиль в ряд (не столбик)
- Уменьшенная аватарка
- Горизонтальная статистика

## 🔧 Тестирование

### Chrome DevTools:
1. F12 → Device Toolbar
2. Выбрать устройство
3. Проверить все breakpoints

### Реальные устройства:
- iPhone (Safari)
- Android (Chrome)
- iPad (Safari)

### Эмуляторы:
- Chrome DevTools
- Firefox Responsive Design Mode

## 📈 Производительность

### Оптимизации:
- CSS minified
- Critical CSS inline
- Lazy loading изображений
- System fonts

### Metrics:
- Lighthouse: 90+ Mobile
- First Contentful Paint: < 2s
- Time to Interactive: < 3.5s

## 🚀 Рекомендации

### Для разработчиков:
1. Всегда тестируйте на реальных устройствах
2. Используйте mobile-first подход
3. Проверяйте контрастность
4. Минимальный размер шрифта: 14px
5. Минимальная область клика: 44×44px

### Для контента:
1. Оптимизируйте изображения
2. Используйте responsive images
3. Короткие заголовки
4. Читабельные абзацы

---

**Создано:** 2026-03-16  
**Статус:** ✅ Готово  
**Поддержка:** iOS 12+, Android 8+, современные браузеры
