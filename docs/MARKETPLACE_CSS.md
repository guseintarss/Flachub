# Marketplace CSS - Документация стилей

## Обзор

Файл `marketplace.css` содержит специализированные стили для маркетплейса PageGlow. Дизайн разработан с учетом следующих принципов:

- **Простота** — чистый и минималистичный интерфейс
- **Удобство** — интуитивная навигация и читаемость
- **Привлекательность** — современный и приятный визуальный стиль
- **Адаптивность** — полная поддержка мобильных устройств

## Цветовая схема

### Светлая тема (по умолчанию)

```
--mp-primary: #0c6acf           (основной синий)
--mp-primary-light: #299cf5     (светлый синий)
--mp-primary-dark: #0852a1      (тёмный синий)
--mp-accent: #10b981            (зелёный, для успеха)
--mp-warning: #f59e0b           (оранжевый, для предупреждения)
--mp-danger: #ef4444            (красный, для ошибок)

--mp-bg: #f7f8fb                (фон страницы)
--mp-surface: #ffffff           (фон компонентов)
--mp-text: #1f2937              (основной текст)
--mp-text-secondary: #6b7280    (вторичный текст)
--mp-border: #e5e7eb            (цвет границ)
```

### Тёмная тема

В тёмном режиме цвета автоматически переходят на более подходящие для глаз:
- Фоны становятся тёмными (#191a1b, #222325)
- Текст становится светлым (#ffffff)
- Все остальные цвета остаются контрастными

## Компоненты

### 1. Header (Заголовок маркета)

```html
<header class="marketplace-header">
    <a href="#" class="marketplace-brand">PageGlow Marketplace</a>
    <nav class="marketplace-nav">
        <a href="#">Ссылка</a>
    </nav>
    <div class="marketplace-header-actions">
        <a href="#" class="btn-marketplace-primary">Кнопка</a>
    </div>
</header>
```

**Классы:**
- `marketplace-header` — контейнер заголовка с градиентным фоном
- `marketplace-brand` — логотип/название маркета
- `marketplace-nav` — навигационные ссылки
- `marketplace-header-actions` — правая часть с кнопками
- `btn-marketplace-primary` — основная кнопка в заголовке

### 2. Hero Section (Героический раздел)

```html
<div class="marketplace-hero">
    <div class="container">
        <h1>Найдите идеального фрилансера</h1>
        <p class="lead">Описание...</p>
    </div>
</div>
```

**Классы:**
- `marketplace-hero` — полноширинный раздел с градиентом и белым текстом

### 3. Projects Grid (Сетка проектов)

```html
<div class="marketplace-projects">
    <div class="project-card">
        <div class="project-card-header">
            <h2 class="project-card-title">
                <a href="#">Название проекта</a>
            </h2>
        </div>
        <div class="project-card-description">
            Описание проекта...
        </div>
        <div class="project-card-footer">
            <span class="project-budget">$500-$1000</span>
            <span class="project-status open">ОТКРЫТ</span>
        </div>
    </div>
</div>
```

**Классы:**
- `marketplace-projects` — сетка (адаптивная)
- `project-card` — карточка проекта с эффектом при наведении
- `project-card-header` — заголовок карточки
- `project-card-title` — название проекта
- `project-card-meta` — метаинформация (бюджет, сроки)
- `project-card-description` — описание
- `project-card-footer` — нижняя часть
- `project-budget` — бюджет проекта
- `project-status` — статус (open, closed, in-progress)
- `project-difficulty` — уровень сложности

### 4. Freelancers Grid (Сетка фрилансеров)

```html
<div class="freelancers-grid">
    <div class="freelancer-card">
        <img src="..." class="freelancer-avatar">
        <h3 class="freelancer-name">Иван Петров</h3>
        <p class="freelancer-title">Веб-разработчик</p>
        <p class="freelancer-bio">Описание...</p>
        
        <div class="freelancer-stats">
            <div class="freelancer-stat">
                <span class="freelancer-stat-value">4.8</span>
                <span class="freelancer-stat-label">Рейтинг</span>
            </div>
        </div>
        
        <div class="freelancer-skills">
            <span class="freelancer-skill">PHP</span>
            <span class="freelancer-skill">JavaScript</span>
        </div>
        
        <div class="freelancer-actions">
            <a href="#" class="btn-primary">Связаться</a>
            <button class="btn-outline">Профиль</button>
        </div>
    </div>
</div>
```

**Классы:**
- `freelancers-grid` — сетка фрилансеров
- `freelancer-card` — карточка фрилансера
- `freelancer-avatar` — аватар фрилансера (круглый)
- `freelancer-name` — имя
- `freelancer-title` — специализация
- `freelancer-bio` — описание
- `freelancer-stats` — статистика
- `freelancer-skills` — навыки
- `freelancer-actions` — кнопки действия

### 5. Project Detail (Деталь проекта)

```html
<div class="project-detail">
    <div class="project-detail-header">
        <h1 class="project-detail-title">Название проекта</h1>
        <div class="project-detail-meta">
            <div class="project-detail-meta-item">
                <i class="fas fa-user"></i> Клиент
            </div>
        </div>
    </div>
    <div class="project-detail-content">
        Полное описание проекта...
    </div>
</div>

<div class="project-sidebar">
    <div class="project-sidebar-card">
        <h3 class="project-sidebar-card-title">Статистика</h3>
        <div class="project-budget-large">$1000</div>
    </div>
</div>
```

**Классы:**
- `project-detail` — основной контейнер деталей
- `project-detail-header` — заголовок с метаинформацией
- `project-detail-title` — заголовок проекта
- `project-detail-meta` — метаинформация
- `project-detail-content` — основной контент
- `project-sidebar` — боковая панель (прилипает при скролле)
- `project-sidebar-card` — карточка в боковой панели

### 6. Forms (Формы)

```html
<form class="marketplace-form">
    <div class="form-group">
        <label for="name">Название</label>
        <input type="text" id="name" name="name">
        <p class="form-help">Максимум 100 символов</p>
    </div>
    
    <div class="form-actions">
        <button type="submit" class="form-btn primary">Отправить</button>
        <button type="button" class="form-btn secondary">Отмена</button>
    </div>
</form>
```

**Классы:**
- `marketplace-form` — контейнер формы
- `form-group` — группа полей
- `form-help` — справочный текст
- `form-error` — ошибка валидации
- `form-actions` — кнопки действия
- `form-btn` — кнопка (primary, secondary)

### 7. Bids (Предложения)

```html
<div class="bids-section">
    <h2 class="bids-section-title">Предложения</h2>
    <div class="bid-card">
        <div class="bid-card-header">
            <span class="bid-amount">$800</span>
            <span class="bid-timeline">5 дней</span>
        </div>
        <div class="bid-freelancer">
            <img src="..." class="bid-freelancer-avatar">
            <span class="bid-freelancer-name">Иван Петров</span>
        </div>
        <p class="bid-message">Сообщение фрилансера...</p>
        <div class="bid-actions">
            <button class="bid-action-btn accept">Принять</button>
            <button class="bid-action-btn decline">Отклонить</button>
        </div>
    </div>
</div>
```

**Классы:**
- `bids-section` — контейнер предложений
- `bid-card` — карточка предложения
- `bid-amount` — сумма предложения
- `bid-timeline` — сроки
- `bid-freelancer` — информация о фрилансере
- `bid-actions` — кнопки действия

### 8. Empty State (Пустое состояние)

```html
<div class="empty-state">
    <div class="empty-state-icon">
        <i class="fas fa-inbox"></i>
    </div>
    <h3 class="empty-state-title">Нет результатов</h3>
    <p class="empty-state-text">Попробуйте изменить фильтры поиска</p>
</div>
```

**Классы:**
- `empty-state` — контейнер пустого состояния
- `empty-state-icon` — иконка
- `empty-state-title` — заголовок
- `empty-state-text` — описание

## Утилиты

### Текст

```html
<p class="text-primary">Синий текст</p>
<p class="text-secondary">Серый текст</p>
<p class="text-danger">Красный текст</p>
<p class="text-success">Зелёный текст</p>
```

### Badges (Значки)

```html
<span class="badge badge-primary">Primary</span>
<span class="badge badge-success">Success</span>
<span class="badge badge-warning">Warning</span>
<span class="badge badge-danger">Danger</span>
```

### Статусы проектов

```html
<span class="project-status open">ОТКРЫТ</span>
<span class="project-status closed">ЗАКРЫТ</span>
<span class="project-status in-progress">В РАБОТЕ</span>
```

## Responsive Design

Стили полностью адаптивны для всех размеров экранов:

- **Desktop (> 768px)** — полная сетка с несколькими колонками
- **Tablet (481px - 768px)** — 2-3 колонки в зависимости от компонента
- **Mobile (≤ 480px)** — одна колонка, все компоненты растянуты на полную ширину

## Анимации

### Slide In Up
```css
.slide-in-up {
  animation: slideInUp 0.3s ease-out;
}
```

### Fade In
```css
.fade-in {
  animation: fadeIn 0.3s ease-out;
}
```

### Loading Spinner
```html
<div class="loading-spinner"></div>
```

## Тень и глубина

- **Стандартная тень:** `var(--mp-shadow)` — для карточек и компонентов
- **Большая тень:** `var(--mp-shadow-lg)` — при наведении, для выделения

## Примеры использования

### Простая карточка проекта

```html
<div class="project-card">
    <div class="project-card-header">
        <h2 class="project-card-title">
            <a href="/project/1/">Разработать мобильное приложение</a>
        </h2>
        <div class="project-card-meta">
            <span>💰 $2000-$3000</span>
            <span>⏱️ 2 недели</span>
        </div>
    </div>
    <div class="project-card-description">
        Нужно разработать мобильное приложение для iOS и Android...
    </div>
    <div class="project-card-footer">
        <span class="project-budget">$2000-$3000</span>
        <span class="project-status open">ОТКРЫТ</span>
        <span class="project-difficulty">Средний</span>
    </div>
</div>
```

### Поисковая форма

```html
<div class="marketplace-search">
    <form method="get">
        <div class="row g-2">
            <div class="col-md-6">
                <input type="text" class="form-control" placeholder="Поиск проектов...">
            </div>
            <div class="col-md-2">
                <select class="form-select">
                    <option>Категория</option>
                </select>
            </div>
            <div class="col-md-4">
                <button type="submit" class="btn-marketplace-primary w-100">
                    <i class="fas fa-search"></i> Поиск
                </button>
            </div>
        </div>
    </form>
</div>
```

## Кастомизация

Для изменения цветов маркета достаточно изменить переменные CSS в `:root`:

```css
:root {
  --mp-primary: #ваш-цвет;
  --mp-accent: #ваш-цвет;
  /* и т.д. */
}
```

## Заметки о дизайне

1. **Минимализм** — избегайте перегруженности элементами, используйте пробелы
2. **Контраст** — убедитесь, что текст хорошо читается на фоне
3. **Согласованность** — используйте одни и те же отступы, радиусы, тени
4. **Микровзаимодействия** — добавляйте эффекты при наведении и клике
5. **Мобильность** — всегда проверяйте на мобильных устройствах

## Поддержка браузеров

CSS использует современные возможности:
- CSS Grid и Flexbox
- CSS переменные (CSS Custom Properties)
- CSS переходы (Transitions)
- CSS анимации (Animations)

Поддерживаются все современные браузеры (Chrome, Firefox, Safari, Edge).
