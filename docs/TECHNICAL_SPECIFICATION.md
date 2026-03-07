# 📋 Техническое задание: Маркетплейс фрилансеров с AI-подбором для PageGlow

## Версия 1.0 | Март 2026

---

## 1. ОБЗОР ПРОЕКТА

### 1.1 Цель и задачи

**Главная цель:** Развить PageGlow из платформы публикации статей в полноценную экосистему, объединяющую:
- Блог с публикацией статей (существующая часть)
- Маркетплейс фрилансеров-разработчиков с AI-подбором
- Раздел "Сообщество" для кросс-продаж и вовлечения

**Ключевые задачи:**
1. Разработка модуля маркетплейса с системой предложений (бидов)
2. Реализация AI-алгоритма для подбора исполнителей
3. Система безопасной сделки с эскроу
4. Встроенный чат с интеграцией Figma/Miro
5. Раздел "Сообщество" с перекрёстными ссылками

### 1.2 Целевая аудитория

| Роль | Описание | Поведение |
|------|---------|-----------|
| **Фрилансер** | Разработчик, дизайнер, DevOps инженер | Ищет проекты, создаёт портфолио, участвует в обсуждениях |
| **Заказчик** | Стартап, малый бизнес, частный клиент | Публикует задачи, управляет проектами, платит через эскроу |
| **Автор** | Разработчик, который пишет статьи | Публикует уроки, делится опытом, привлекает фрилансеров |
| **Читатель** | Начинающий специалист, энтузиаст | Читает статьи, смотрит кейсы, может стать фрилансером |

### 1.3 Модель монетизации

```
Доход платформы:
├─ Комиссия с проектов: 5-15% от суммы
├─ Премиум подписка фрилансеров:
│  ├─ Базовый: $0/мес (бесплатно)
│  ├─ Pro: $9/мес (повышенный рейтинг)
│  └─ Expert: $29/мес (расширенная аналитика)
├─ Спонсорские статьи: $500-2000/пост
└─ Реклама в разделе "Сообщество": $1000+/мес
```

---

## 2. АРХИТЕКТУРА СИСТЕМЫ

### 2.1 Структура приложения Django

```
PageGlow/
├── PageGlow/           # Проект
│   ├── settings.py    # Конфигурация
│   ├── urls.py        # Маршруты
│   └── wsgi.py
├── main/              # Блог (существует)
├── users/             # Пользователи (существует)
├── marketplace/       # 🆕 МАРКЕТПЛЕЙС
│   ├── models.py     # Модели (Project, Bid, Payment, etc.)
│   ├── views.py      # Представления
│   ├── forms.py      # Формы
│   ├── urls.py       # Маршруты
│   ├── admin.py      # Админ-панель
│   └── migrations/
└── community/        # 🆕 СООБЩЕСТВО
    ├── models.py    # Модели (CommunityPost, CommunityComment)
    ├── views.py     # Представления
    ├── forms.py     # Формы
    ├── urls.py      # Маршруты
    └── admin.py     # Админ-панель
```

### 2.2 Модели данных (Marketplace)

#### **Skill** - Навыки/технологии
```python
Skill:
  - name: CharField (unique)         # "Python"
  - slug: SlugField (unique)         # "python"
  - category: CharField              # "language", "framework", "tool", "database"
  - icon: CharField                  # "fab fa-python"
```

#### **FreelancerProfile** - Профиль фрилансера
```python
FreelancerProfile:
  - user: OneToOne(User)
  - role: CharField                  # "backend", "frontend", "fullstack", etc.
  - bio: TextField (max 1000)
  - avatar: ImageField
  - years_experience: IntegerField
  - skills: ManyToMany(Skill)
  - portfolio_url, github_url, linkedin_url: URLField
  - rating: FloatField (0-5)         # На основе отзывов
  - total_reviews, total_projects, total_earned: IntegerField
  - is_verified: BooleanField        # Проверен ли модератором
  - is_available: BooleanField       # Доступен для новых проектов
  - hourly_rate: DecimalField (опционально)
  - created_at, updated_at: DateTimeField
```

#### **Project** - Проект на маркетплейсе
```python
Project:
  - id: UUIDField (primary key)
  - title, description: CharField/TextField
  - client: ForeignKey(User)         # Кто создал
  - required_skills: ManyToMany(Skill)
  - budget_min, budget_max: DecimalField
  - budget_type: CharField           # "fixed" или "hourly"
  - currency: CharField              # "RUB", "USD"
  - deadline: DateTimeField
  - status: CharField                # "draft", "published", "in_progress", "completed"
  - assigned_to: ForeignKey(User, nullable)  # Выбранный фрилансер
  - category: CharField              # "web", "mobile", "data", "devops", "design"
  - difficulty: CharField            # "easy", "medium", "hard"
  - is_urgent: BooleanField
  - budget_remaining: DecimalField   # Динамически рассчитывается
  - created_at, updated_at: DateTimeField
  
  Methods:
  - ai_matching_score(freelancer_user) -> float  # AI-оценка совместимости
  - get_active_bids() -> QuerySet    # Активные предложения
```

#### **Bid** - Предложение на проект
```python
Bid:
  - id: UUIDField (primary key)
  - project: ForeignKey(Project)
  - freelancer: ForeignKey(User)
  - proposed_price: DecimalField
  - estimated_days: IntegerField
  - cover_letter: TextField (max 2000)
  - ai_score: FloatField            # Рассчитывается при создании (0-100)
  - status: CharField               # "pending", "accepted", "rejected", "withdrawn"
  - created_at, updated_at: DateTimeField
  
  Meta:
  - unique_together: [project, freelancer]  # Один фрилансер - одно предложение
  - ordering: ['-ai_score', '-created_at']  # Сортировка по AI-оценке
```

#### **Payment** - Платёж/эскроу
```python
Payment:
  - id: UUIDField
  - project: ForeignKey(Project)
  - amount: DecimalField
  - status: CharField              # "pending", "processing", "completed", "refunded"
  - payment_method: CharField      # "stripe", "paypal", "crypto"
  - transaction_id: CharField (unique)
  - created_at, updated_at: DateTimeField
```

#### **Milestone** - Этапы проекта
```python
Milestone:
  - id: UUIDField
  - project: ForeignKey(Project)
  - title, description: CharField/TextField
  - amount: DecimalField           # Сумма для этого этапа
  - deadline: DateTimeField
  - status: CharField              # "pending", "in_progress", "completed", "approved"
  - created_at, updated_at: DateTimeField
```

#### **ProjectChat** - Чат проекта
```python
ProjectChat:
  - id: UUIDField
  - project: OneToOne(Project)
  - created_at: DateTimeField

ChatMessage:
  - id: UUIDField
  - chat: ForeignKey(ProjectChat)
  - sender: ForeignKey(User)
  - content: TextField
  - attachments: JSONField         # Массив файлов
  - embedded_url: URLField (опция) # Figma/Miro
  - embedded_type: CharField       # "figma", "miro", "other"
  - created_at, updated_at: DateTimeField
```

#### **Review** - Отзыв после проекта
```python
Review:
  - id: UUIDField
  - project: ForeignKey(Project)
  - reviewer: ForeignKey(User)     # Кто оставил отзыв
  - reviewed_user: ForeignKey(User) # На кого отзыв
  - rating: IntegerField (1-5)
  - comment: TextField (max 1000)
  - quality, communication, deadline_adherence, professionalism: IntegerField
  - created_at, updated_at: DateTimeField
```

#### **Dispute** - Спор
```python
Dispute:
  - id: UUIDField
  - project: ForeignKey(Project)
  - initiator: ForeignKey(User)    # Кто начал спор
  - respondent: ForeignKey(User)   # Кто отвечает
  - subject, description: CharField/TextField
  - status: CharField              # "open", "in_review", "resolved", "closed"
  - resolution: TextField
  - resolved_at: DateTimeField
  - created_at, updated_at: DateTimeField
```

### 2.3 Модели данных (Community)

#### **CommunityPost** - Пост в сообществе
```python
CommunityPost:
  - id: UUIDField
  - title: CharField (max 300)
  - content: TextField
  - author: ForeignKey(User)
  - post_type: CharField           # "case_study", "tutorial", "tip", "project", "story", "discussion"
  - category: CharField            # "backend", "frontend", "mobile", "devops", "design", "data", "career", "tools"
  - tags: CharField                # Разделённые запятой
  - related_article: ForeignKey(Post, nullable)    # Ссылка на основной блог
  - related_marketplace_project: ForeignKey(Project, nullable)
  - cover_image: ImageField
  - attachments: JSONField
  - views_count, likes_count, comments_count: IntegerField
  - is_published: BooleanField
  - is_featured: BooleanField      # Закреплённый пост
  - is_moderated: BooleanField
  - moderated_by: ForeignKey(User, nullable)
  - created_at, updated_at: DateTimeField
```

#### **CommunityComment** - Комментарий
```python
CommunityComment:
  - id: UUIDField
  - post: ForeignKey(CommunityPost)
  - author: ForeignKey(User)
  - content: TextField
  - parent_comment: ForeignKey(self, nullable)  # Для ответов
  - likes_count: IntegerField
  - is_published, is_pinned: BooleanField
  - created_at, updated_at: DateTimeField
```

#### **CommunityModerator** - Модератор
```python
CommunityModerator:
  - user: OneToOne(User)
  - bio: TextField
  - can_moderate_posts, can_moderate_comments, can_feature_posts: BooleanField
  - created_at: DateTimeField
```

#### **ContentPlan** - План контента
```python
ContentPlan:
  - title, description: CharField/TextField
  - category: CharField
  - status: CharField              # "planned", "in_progress", "ready", "published", "cancelled"
  - assigned_to: ForeignKey(User, nullable)
  - planned_date, publication_date: DateField
  - priority: CharField            # "low", "normal", "high"
  - published_post: ForeignKey(CommunityPost, nullable)
  - created_at, updated_at: DateTimeField
```

---

## 3. AI-АЛГОРИТМ ПОДБОРА

### 3.1 Формула расчёта совместимости

```python
def ai_matching_score(project, freelancer) -> float:
    """Рассчитать AI-оценку совместимости (0-100)"""
    
    score = 0
    
    # 1. СОВПАДЕНИЕ НАВЫКОВ (40 баллов) ⭐⭐⭐⭐
    project_skills = set(project.required_skills.all())
    freelancer_skills = set(freelancer.skills.all())
    
    if project_skills:
        skill_match_ratio = len(project_skills & freelancer_skills) / len(project_skills)
        score += skill_match_ratio * 40
    else:
        score += 40  # Если нет требований, даём полный балл
    
    # 2. ОПЫТ (20 баллов) ⭐⭐
    if project.difficulty == "easy":
        score += 20
    elif project.difficulty == "medium":
        if freelancer.years_experience >= 1:
            score += 20
        elif freelancer.years_experience >= 0.5:
            score += 15
        else:
            score += 5
    elif project.difficulty == "hard":
        if freelancer.years_experience >= 3:
            score += 20
        elif freelancer.years_experience >= 1:
            score += 15
        else:
            score += 0
    
    # 3. РЕЙТИНГ (20 баллов) ⭐⭐
    rating_score = (freelancer.rating / 5) * 20  # Если рейтинг 5, то 20 баллов
    score += rating_score
    
    # 4. ДОСТУПНОСТЬ (10 баллов) ⭐
    if freelancer.is_available:
        score += 10
    
    # 5. ВЕРИФИКАЦИЯ (10 баллов БОНУС) ⭐
    if freelancer.is_verified:
        score += 10  # Может превышать 100, но потом cap
    
    return min(100, score)  # Максимум 100 баллов
```

### 3.2 Примеры расчётов

**Пример 1: Идеальный кандидат**
```
Проект: Backend API на Python (средняя сложность)
Фрилансер: Python разработчик, 3 года опыта, рейтинг 4.8, верифицирован

Расчёт:
- Навыки: 100% совпадение → 40 баллов
- Опыт: 3 года (≥1) → 20 баллов
- Рейтинг: 4.8/5 → 19.2 баллов
- Доступность: Да → 10 баллов
- Верификация: Да → 10 баллов
───────────────────────
TOTAL: 99.2 ✅ ОТЛИЧНЫЙ КАНДИДАТ
```

**Пример 2: Начинающий разработчик**
```
Проект: Frontend на React (средняя сложность)
Фрилансер: Выпускник буткемпа, React знает, 0.3 года опыта, рейтинг 4.0

Расчёт:
- Навыки: 100% совпадение → 40 баллов
- Опыт: <0.5 года → 5 баллов
- Рейтинг: 4.0/5 → 16 баллов
- Доступность: Да → 10 баллов
- Верификация: Нет → 0 баллов
───────────────────────
TOTAL: 71 🟡 СРЕДНИЙ КАНДИДАТ
```

### 3.3 Интеграция с GitHub

**Будущее расширение:**
```python
def analyze_github_profile(freelancer_user):
    """Анализ GitHub для дополнительных баллов"""
    # Получить список репозиториев
    # Анализировать: количество звёзд, активность, качество кода
    # Добавлять бонусные баллы к ai_score
    pass
```

---

## 4. API ENDPOINTS

### 4.1 Маркетплейс

#### Projects (Проекты)
```
GET    /api/marketplace/projects/               # Список проектов (с фильтрацией)
POST   /api/marketplace/projects/               # Создать проект
GET    /api/marketplace/projects/{id}/          # Детали проекта
PUT    /api/marketplace/projects/{id}/          # Обновить проект
DELETE /api/marketplace/projects/{id}/          # Удалить проект
POST   /api/marketplace/projects/{id}/publish/  # Опубликовать проект
```

#### Bids (Предложения)
```
GET    /api/marketplace/bids/                   # Мои предложения
POST   /api/marketplace/projects/{id}/bid/      # Создать предложение
GET    /api/marketplace/bids/{id}/              # Детали предложения
PUT    /api/marketplace/bids/{id}/              # Обновить предложение (статус)
DELETE /api/marketplace/bids/{id}/              # Отозвать предложение
POST   /api/marketplace/bids/{id}/accept/       # Принять предложение (для заказчика)
POST   /api/marketplace/bids/{id}/reject/       # Отклонить предложение
```

#### Freelancers (Фрилансеры)
```
GET    /api/marketplace/freelancers/            # Список фрилансеров (с фильтрацией)
GET    /api/marketplace/freelancers/{id}/       # Профиль фрилансера
PUT    /api/marketplace/freelancers/{id}/       # Обновить профиль
POST   /api/marketplace/freelancers/{id}/skills/  # Добавить навыки
```

#### Chat (Чат)
```
GET    /api/marketplace/projects/{id}/chat/     # История чата
POST   /api/marketplace/projects/{id}/chat/     # Отправить сообщение
WS     /ws/marketplace/chat/{project_id}/      # WebSocket для real-time чата
```

#### Reviews (Отзывы)
```
POST   /api/marketplace/projects/{id}/review/   # Оставить отзыв
GET    /api/marketplace/reviews/{freelancer_id}/ # Отзывы на фрилансера
```

#### Payments (Платежи)
```
POST   /api/marketplace/projects/{id}/payment/  # Инициировать платёж
GET    /api/marketplace/payments/{id}/          # Статус платежа
POST   /api/marketplace/payments/{id}/refund/   # Вернуть платёж
```

### 4.2 Сообщество

#### Posts (Посты)
```
GET    /api/community/posts/                    # Список постов
POST   /api/community/posts/                    # Создать пост
GET    /api/community/posts/{id}/               # Детали поста
PUT    /api/community/posts/{id}/               # Обновить пост
DELETE /api/community/posts/{id}/               # Удалить пост
GET    /api/community/posts/{id}/comments/      # Комментарии к посту
```

#### Comments (Комментарии)
```
POST   /api/community/posts/{id}/comments/      # Создать комментарий
PUT    /api/community/comments/{id}/            # Обновить комментарий
DELETE /api/community/comments/{id}/            # Удалить комментарий
POST   /api/community/comments/{id}/like/       # Лайкнуть комментарий
```

#### Likes (Лайки)
```
POST   /api/community/posts/{id}/like/          # Лайкнуть пост
DELETE /api/community/posts/{id}/like/          # Удалить лайк
```

---

## 5. БЕЗОПАСНОСТЬ И АУТЕНТИФИКАЦИЯ

### 5.1 Аутентификация

```
Методы:
├─ Django Session Auth     (веб-формы)
├─ JWT (Djoser)           (API)
├─ OAuth 2.0              (Google, GitHub) 🔜
└─ 2FA (Two-Factor Auth)  🔜
```

### 5.2 Permissions (Разрешения)

```python
# Marketplace
- Фрилансер может:
  ✓ Просматривать публичные проекты
  ✓ Создавать предложения (если верифицирован)
  ✓ Редактировать собственный профиль
  ✓ Участвовать в чатах собственных проектов

- Заказчик может:
  ✓ Создавать проекты
  ✓ Редактировать свои проекты
  ✓ Просматривать и принимать предложения
  ✓ Оставлять отзывы
  ✓ Управлять платежами

- Админ может:
  ✓ Модерировать контент
  ✓ Верифицировать фрилансеров
  ✓ Разрешать споры
  ✓ Управлять комиссиями
```

### 5.3 Защита от атак

```
Меры:
├─ HTTPS/TLS 1.3 (обязательно)
├─ CSRF protection (Django)
├─ SQL Injection protection (ORM)
├─ XSS protection (шаблоны)
├─ Rate limiting (для API)
└─ Content Security Policy (CSP)
```

---

## 6. ИНТЕГРАЦИИ

### 6.1 Платежи (Stripe)

```python
# Процесс:
1. Клиент создаёт проект и резервирует бюджет
2. Платёж в статусе "pending"
3. Фрилансер принимается, платёж "processing"
4. При завершении проекта → "completed" (переводим фрилансеру)
5. При отказе → "refunded" (возвращаем клиенту)

API:
POST /api/payments/create-intent/        # Создать intent
POST /api/payments/confirm/              # Подтвердить платёж
GET  /api/payments/{id}/status/          # Проверить статус
```

### 6.2 Figma / Miro (встраивание превью)

```javascript
// В чате проекта пользователь может поделиться:
- Figma Design: https://figma.com/file/...
  → Автоматически показываем превью

- Miro Board: https://miro.com/app/board/...
  → Встраиваем интерактивную доску

// Реализация:
<iframe src="https://www.figma.com/embed?embed_host=share&url={url}" />
<iframe src="https://miro.com/app/embed/..." />
```

### 6.3 GitHub API (анализ кода)

```python
# Будущая фишка:
1. Фрилансер связывает свой GitHub
2. Мы анализируем его репозитории
3. Считаем: кол-во звёзд, активность, качество кода
4. Добавляем бонусные баллы к ai_score

Требует:
- github.com OAuth интеграция
- Backend для парсинга Git API
- ML модель для оценки качества кода
```

---

## 7. ПЛАН РАЗРАБОТКИ

### Фаза 1: MVP (4 недели)

- [x] **Неделя 1-2**: Модели + Admin панель
- [ ] **Неделя 2-3**: Views + Templates (Marketplace)
- [ ] **Неделя 3-4**: Формы + URL маршруты
- [ ] **Неделя 4**: Базовая AI-оценка + тестирование

### Фаза 2: Продвинутые функции (3 недели)

- [ ] **Неделя 1**: Чат + WebSocket
- [ ] **Неделя 2**: Платежи (Stripe интеграция)
- [ ] **Неделя 3**: Раздел Сообщество

### Фаза 3: Оптимизация (2 недели)

- [ ] **Неделя 1**: Performance + Caching
- [ ] **Неделя 2**: SEO + Analytics

**Общий срок: 9 недель (~2 месяца)**

---

## 8. ТРЕБОВАНИЯ К ОКРУЖЕНИЮ

### Backend

```
Django 6.0+
Python 3.10+
PostgreSQL 14+
Redis (для кеша и очередей)
```

### Frontend

```
React 18+ (для интерактивных элементов)
Bootstrap 5+ (уже используется)
Tailwind CSS (опционально)
```

### Зависимости Python

```
djangorestframework==3.16+
djoser==2.3+
stripe==5.0+  (добавить)
pillow==12+   (для изображений)
celery==5.3+  (для async задач)  🔜
django-cors-headers==4.0+
channels==4.0+  (для WebSocket)  🔜
```

---

## 9. ПОКАЗАТЕЛИ УСПЕХА (KPI)

```
Маркетплейс:
├─ 100+ фрилансеров на платформе
├─ 50+ активных проектов
├─ 70%+ успешных сделок (без споров)
├─ Средний рейтинг: 4.5+ звёзд
└─ Комиссия: $5,000+/месяц

Сообщество:
├─ 200+ постов
├─ 10,000+ просмотров/месяц
├─ 500+ активных читателей
└─ 100+ лайков/месяц

Общее:
├─ 5,000+ зарегистрированных пользователей
├─ 1,000+ активных пользователей/месяц
└─ 90%+ uptime
```

---

## 10. РИСКИ И РЕШЕНИЯ

| Риск | Вероятность | Решение |
|------|-------------|---------|
| Освоение Django сложнее чем ожидалось | Средняя | Использовать готовые пакеты (djoser, django-rest-framework) |
| Сложность с WebSocket для чата | Средняя | Использовать Django Channels или внешний сервис (Socket.io) |
| Интеграция Stripe требует PCI compliance | Средняя | Использовать Stripe Payment Intent API |
| AI-алгоритм может быть неточным | Низкая | Начать с простого, улучшать на основе данных |
| Мошенничество на платформе | Средняя | Верификация фрилансеров, споры, система рейтингов |

---

**Автор:** AI Assistant  
**Дата:** Март 2026  
**Статус:** 🟡 На разработку
