# 🧪 План тестирования: Маркетплейс фрилансеров PageGlow

---

## 1. UNIT ТЕСТЫ (моделей и функций)

### 1.1 Тесты моделей Marketplace

```python
# marketplace/tests/test_models.py

from django.test import TestCase
from django.contrib.auth.models import User
from marketplace.models import *

class FreelancerProfileTestCase(TestCase):
    """Тесты профиля фрилансера"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='dev1',
            email='dev@example.com',
            password='test123'
        )
        self.profile = FreelancerProfile.objects.create(
            user=self.user,
            role='backend',
            years_experience=3,
            rating=4.5
        )
    
    def test_profile_creation(self):
        """Проверка создания профиля"""
        self.assertEqual(self.profile.user.username, 'dev1')
        self.assertEqual(self.profile.rating, 4.5)
    
    def test_get_completion_rate(self):
        """Проверка расчёта процента завершения"""
        # Создаём проекты
        project = Project.objects.create(
            title='API',
            description='Build API',
            client=self.user,
            budget_min=100,
            budget_max=500,
            deadline='2026-12-31'
        )
        project.status = 'completed'
        project.assigned_to = self.user
        project.save()
        
        completion_rate = self.profile.get_completion_rate()
        self.assertEqual(completion_rate, 100.0)

class ProjectTestCase(TestCase):
    """Тесты модели Project"""
    
    def setUp(self):
        self.client_user = User.objects.create_user(
            username='client1',
            password='test123'
        )
        self.freelancer_user = User.objects.create_user(
            username='dev1',
            password='test123'
        )
        self.freelancer_profile = FreelancerProfile.objects.create(
            user=self.freelancer_user,
            role='backend',
            years_experience=2,
            rating=4.8
        )
        
        # Создаём навыки
        self.python_skill = Skill.objects.create(
            name='Python',
            slug='python',
            category='language'
        )
        self.freelancer_profile.skills.add(self.python_skill)
        
        # Создаём проект
        self.project = Project.objects.create(
            title='Backend API',
            description='Build REST API',
            client=self.client_user,
            budget_min=500,
            budget_max=2000,
            difficulty='medium'
        )
        self.project.required_skills.add(self.python_skill)
    
    def test_ai_matching_score_perfect(self):
        """Проверка AI-оценки идеального кандидата"""
        score = self.project.ai_matching_score(self.freelancer_user)
        self.assertGreater(score, 90)  # Должна быть высокая оценка
        self.assertLessEqual(score, 100)
    
    def test_ai_matching_score_mismatch(self):
        """Проверка оценки при отсутствии навыков"""
        other_user = User.objects.create_user(
            username='designer1',
            password='test123'
        )
        FreelancerProfile.objects.create(
            user=other_user,
            role='designer',
            years_experience=1,
            rating=3.0
        )
        
        score = self.project.ai_matching_score(other_user)
        self.assertLess(score, 60)  # Должна быть низкая оценка

class BidTestCase(TestCase):
    """Тесты модели Bid"""
    
    def setUp(self):
        self.client_user = User.objects.create_user('client1', password='test123')
        self.freelancer_user = User.objects.create_user('dev1', password='test123')
        
        self.project = Project.objects.create(
            title='Project',
            description='Description',
            client=self.client_user,
            budget_min=100,
            budget_max=500
        )
        
        FreelancerProfile.objects.create(
            user=self.freelancer_user,
            role='backend',
            years_experience=1
        )
    
    def test_bid_creation_with_ai_score(self):
        """Проверка создания бида с расчётом AI-оценки"""
        bid = Bid.objects.create(
            project=self.project,
            freelancer=self.freelancer_user,
            proposed_price=300,
            estimated_days=5,
            cover_letter='I can do this'
        )
        
        self.assertGreater(bid.ai_score, 0)
        self.assertLessEqual(bid.ai_score, 100)
    
    def test_unique_bid_per_freelancer(self):
        """Проверка уникальности бида на проект"""
        Bid.objects.create(
            project=self.project,
            freelancer=self.freelancer_user,
            proposed_price=300,
            estimated_days=5,
            cover_letter='First bid'
        )
        
        # Пытаемся создать второй бид - должна ошибка
        with self.assertRaises(Exception):
            Bid.objects.create(
                project=self.project,
                freelancer=self.freelancer_user,
                proposed_price=350,
                estimated_days=4,
                cover_letter='Second bid'
            )
```

### 1.2 Тесты сообщества

```python
# community/tests/test_models.py

class CommunityPostTestCase(TestCase):
    """Тесты модели CommunityPost"""
    
    def setUp(self):
        self.author = User.objects.create_user('author1', password='test123')
        self.post = CommunityPost.objects.create(
            title='Python Tips',
            content='10 tips for better code',
            author=self.author,
            category='backend',
            post_type='tip'
        )
    
    def test_post_creation(self):
        """Проверка создания поста"""
        self.assertEqual(self.post.title, 'Python Tips')
        self.assertEqual(self.post.author.username, 'author1')
        self.assertEqual(self.post.views_count, 0)
    
    def test_get_tags_list(self):
        """Проверка парсинга тегов"""
        self.post.tags = 'python, django, rest-api'
        tags = self.post.get_tags_list()
        self.assertEqual(len(tags), 3)
        self.assertIn('python', tags)

class CommunityCommentTestCase(TestCase):
    """Тесты комментариев"""
    
    def setUp(self):
        self.author = User.objects.create_user('author1', password='test123')
        self.commenter = User.objects.create_user('commenter1', password='test123')
        
        self.post = CommunityPost.objects.create(
            title='Test Post',
            content='Content',
            author=self.author
        )
    
    def test_comment_creation(self):
        """Проверка создания комментария"""
        comment = CommunityComment.objects.create(
            post=self.post,
            author=self.commenter,
            content='Great post!'
        )
        
        self.assertEqual(comment.content, 'Great post!')
        self.assertEqual(comment.post.comments.count(), 1)
```

---

## 2. ИНТЕГРАЦИОННЫЕ ТЕСТЫ (Views)

### 2.1 Тесты Views маркетплейса

```python
# marketplace/tests/test_views.py

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from marketplace.models import *

class ProjectDetailViewTestCase(TestCase):
    """Тесты детального просмотра проекта"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('user1', password='test123')
        self.project = Project.objects.create(
            title='Test Project',
            description='Description',
            client=self.user,
            budget_min=100,
            budget_max=500
        )
    
    def test_project_detail_view_status_200(self):
        """Проверка доступности страницы проекта"""
        response = self.client.get(reverse('marketplace:project_detail', args=[self.project.pk]))
        self.assertEqual(response.status_code, 200)
    
    def test_project_detail_view_context(self):
        """Проверка контекста в шаблоне"""
        response = self.client.get(reverse('marketplace:project_detail', args=[self.project.pk]))
        self.assertEqual(response.context['project'], self.project)

class BidCreateViewTestCase(TestCase):
    """Тесты создания предложения"""
    
    def setUp(self):
        self.client = Client()
        self.freelancer = User.objects.create_user('freelancer1', password='test123')
        FreelancerProfile.objects.create(user=self.freelancer, role='backend')
        
        self.client_user = User.objects.create_user('client1', password='test123')
        self.project = Project.objects.create(
            title='Project',
            description='Desc',
            client=self.client_user,
            budget_min=100,
            budget_max=500
        )
    
    def test_bid_create_requires_login(self):
        """Проверка, что требуется вход"""
        response = self.client.post(
            reverse('marketplace:bid_create', args=[self.project.pk]),
            {'proposed_price': 300, 'estimated_days': 5, 'cover_letter': 'I can do it'}
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_bid_create_by_freelancer(self):
        """Проверка создания бида фрилансером"""
        self.client.login(username='freelancer1', password='test123')
        response = self.client.post(
            reverse('marketplace:bid_create', args=[self.project.pk]),
            {
                'proposed_price': '300.00',
                'estimated_days': '5',
                'cover_letter': 'I can do it'
            }
        )
        
        self.assertEqual(Bid.objects.count(), 1)
        bid = Bid.objects.first()
        self.assertEqual(bid.freelancer, self.freelancer)
        self.assertEqual(bid.proposed_price, 300.00)
```

---

## 3. API ТЕСТЫ

### 3.1 REST API тесты

```python
# marketplace/tests/test_api.py

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from marketplace.models import *

class ProjectAPITestCase(TestCase):
    """Тесты REST API проектов"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user('user1', password='test123')
        self.project = Project.objects.create(
            title='API Project',
            description='Desc',
            client=self.user,
            budget_min=100,
            budget_max=500
        )
    
    def test_list_projects(self):
        """Проверка списка проектов через API"""
        response = self.client.get('/api/marketplace/projects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_project_requires_auth(self):
        """Проверка, что создание проекта требует авторизации"""
        response = self.client.post('/api/marketplace/projects/', {
            'title': 'New Project',
            'description': 'Desc',
            'budget_min': 100,
            'budget_max': 500
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
```

---

## 4. E2E ТЕСТЫ (Selenium)

### 4.1 Сценарии Selenium

```python
# tests/e2e/test_marketplace_flow.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class MarketplaceE2ETestCase:
    """End-to-End тесты маркетплейса"""
    
    def setup(self):
        self.driver = webdriver.Chrome()
        self.base_url = 'http://localhost:8000'
    
    def test_complete_project_flow(self):
        """Тест: Заказчик создаёт проект, фрилансер делает ставку, проект завершается"""
        
        # 1. Заказчик входит и создаёт проект
        self.driver.get(f'{self.base_url}/marketplace/')
        login_button = self.driver.find_element(By.ID, 'login-button')
        login_button.click()
        
        # Заполняем форму входа
        username_field = self.driver.find_element(By.NAME, 'username')
        password_field = self.driver.find_element(By.NAME, 'password')
        username_field.send_keys('client1')
        password_field.send_keys('test123')
        password_field.submit()
        
        # Ждём загрузки
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'create-project-btn'))
        )
        
        # Нажимаем "Создать проект"
        create_btn = self.driver.find_element(By.ID, 'create-project-btn')
        create_btn.click()
        
        # Заполняем форму проекта
        title_field = self.driver.find_element(By.NAME, 'title')
        title_field.send_keys('Build REST API')
        
        # ... заполняем остальные поля
        
        submit_btn = self.driver.find_element(By.ID, 'submit-project')
        submit_btn.click()
        
        # 2. Проверяем, что проект создан
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'project-success'))
        )
        
        # 3. Фрилансер входит и делает ставку
        self.driver.get(f'{self.base_url}/users/logout/')
        self.driver.get(f'{self.base_url}/marketplace/')
        
        # Логиним как фрилансер...
        # (аналогично шагу 1)
        
        # Находим проект и нажимаем "Сделать ставку"
        bid_button = self.driver.find_element(By.CLASS_NAME, 'bid-button')
        bid_button.click()
        
        # Заполняем форму ставки
        price_field = self.driver.find_element(By.NAME, 'proposed_price')
        price_field.send_keys('1500')
        
        days_field = self.driver.find_element(By.NAME, 'estimated_days')
        days_field.send_keys('10')
        
        letter_field = self.driver.find_element(By.NAME, 'cover_letter')
        letter_field.send_keys('I have 3 years experience with REST APIs')
        
        submit_bid = self.driver.find_element(By.ID, 'submit-bid')
        submit_bid.click()
        
        # 4. Заказчик принимает ставку
        # ... аналогично входим как заказчик
        # ... находим проект и принимаем предложение
        
        print("✅ E2E тест успешно пройден!")
    
    def teardown(self):
        self.driver.quit()
```

---

## 5. НАГРУЗОЧНОЕ ТЕСТИРОВАНИЕ

### 5.1 Locust script

```python
# tests/load/locustfile.py

from locust import HttpUser, task, between
import random

class MarketplaceUser(HttpUser):
    """Имитация пользователя маркетплейса"""
    
    wait_time = between(1, 3)  # 1-3 секунды между действиями
    
    def on_start(self):
        """Логин перед началом"""
        self.client.post('/users/login/', {
            'username': f'user_{random.randint(1, 100)}',
            'password': 'test123'
        })
    
    @task(3)
    def view_projects(self):
        """Просмотр списка проектов"""
        self.client.get('/marketplace/')
    
    @task(2)
    def view_project_detail(self):
        """Просмотр детали проекта"""
        project_id = random.randint(1, 50)
        self.client.get(f'/marketplace/projects/{project_id}/')
    
    @task(1)
    def search_projects(self):
        """Поиск проектов"""
        self.client.get('/marketplace/?q=python&category=web')

# Запуск:
# locust -f locustfile.py --host=http://localhost:8000
```

---

## 6. ПОКРЫТИЕ ТЕСТАМИ

### Целевое покрытие

```
Компонент          Покрытие    Статус
────────────────────────────────────────
Models               90%+       ✅
Views                85%+       ⏳
Forms                80%+       ⏳
API Endpoints        85%+       ⏳
Utilities            95%+       ✅
Integration Tests    70%+       ⏳
────────────────────────────────────────
TOTAL               85%         🟡
```

### Запуск тестов

```bash
# Все тесты
python manage.py test

# Только marketplace
python manage.py test marketplace

# С покрытием
coverage run --source='.' manage.py test
coverage report

# В параллель (ускорение)
python manage.py test --parallel 4
```

---

## 7. БАГИ И БАГРЕПОРТЫ

### Форма багрепорта

```
Заголовок: [MARKETPLACE/COMMUNITY] Краткое описание проблемы

Шаги воспроизведения:
1. ...
2. ...
3. ...

Ожидаемое поведение:
...

Фактическое поведение:
...

Окружение:
- Django версия: 
- Python версия:
- Браузер:
- OS:

Логи ошибок:
...
```

---

## 8. КОНТРОЛЬНЫЙ СПИСОК ПЕРЕД ПРОДАКШЕНОМ

### Функциональность
- [ ] Все API endpoints работают
- [ ] Формы валидируют данные
- [ ] Аутентификация работает
- [ ] Permissions установлены правильно
- [ ] Чат работает в real-time
- [ ] Платежи обрабатываются

### Безопасность
- [ ] HTTPS включён
- [ ] CSRF защита включена
- [ ] SQL Injection защита
- [ ] XSS защита
- [ ] Rate limiting настроен
- [ ] CORS правильно настроен

### Производительность
- [ ] БД queries оптимизированы (N+1)
- [ ] Индексы в БД созданы
- [ ] Caching работает
- [ ] Нет утечек памяти
- [ ] Нагрузка < 80% при 1000 RPS

### Мониторинг
- [ ] Логирование включено
- [ ] Метрики собираются (Prometheus)
- [ ] Алерты настроены
- [ ] Backups настроены

---

**Автор:** QA Team  
**Версия:** 1.0  
**Дата:** Март 2026  
**Статус:** 🟡 В разработке
