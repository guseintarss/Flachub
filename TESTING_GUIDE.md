# 🧪 Тестирование в PageGlow - Руководство

## ✅ Что настроено

В проект добавлена полноценная система тестирования:

### Установленные пакеты
- **pytest** 8.3.5 - фреймворк для тестирования
- **pytest-django** 4.11.1 - интеграция с Django
- **pytest-cov** 6.0.0 - отчет о покрытии кода
- **factory-boy** 3.3.3 - фабрики тестовых данных
- **faker** 37.1.0 - генерация случайных данных

### Созданные файлы
```
PageGlow/
├── conftest.py              # Общие фикстуры для всех тестов
├── pytest.ini               # Конфигурация pytest
├── tests/
│   ├── README.md            # Документация по тестам
│   ├── __init__.py
│   ├── test_models.py       # 37 тестов моделей (✅ работают)
│   ├── test_views.py        # Тесты представлений
│   └── test_api.py          # Тесты API endpoints
├── ..github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions для CI/CD
├── Makefile                 # Команды для управления тестами
└── run_tests.bat            # Скрипт для Windows
```

## 🚀 Быстрый старт

### Запуск тестов (Windows)
```bash
# Все тесты
run_tests.bat

# С покрытием
run_tests.bat cov

# HTML отчет
run_tests.bat html

# Только модели
run_tests.bat models

# Только views
run_tests.bat views

# Только API
run_tests.bat api

# Очистка
run_tests.bat clean
```

### Запуск тестов (Linux/Mac через Makefile)
```bash
make test              # Все тесты
make test-cov          # С покрытием
make test-unit         # Только unit
make test-views        # Только views
make test-api          # Только API
```

### Запуск через pytest напрямую
```bash
# Все тесты
pytest

# Конкретный файл
pytest tests/test_models.py -v

# Один тест
pytest tests/test_models.py::TestUserModel::test_user_creation -v

# С покрытием
pytest --cov=PageGlow --cov-report=html

# Кроме медленных тестов
pytest -m "not slow"
```

## 📊 Результаты тестов

### Model Tests (37 тестов)
✅ **Все тесты проходят**

Протестированные модели:
- **User** - 9 тестов (создание, подписки, лайки)
- **Post** - 10 тестов (статьи, лайки, просмотры)
- **Category** - 4 теста
- **Tag** - 3 теста
- **Comment** - 3 теста
- **Subscription** - 3 теста
- **Notification** - 3 теста
- **Rule** - 2 теста

**Покрытие кода:** ~83%

## 📁 Структура тестов

### Фикстуры (conftest.py)

**Пользователи:**
- `user` - стандартный пользователь
- `another_user` - другой пользователь
- `admin_user` - суперпользователь
- `user_factory` - фабрика пользователей

**Клиенты:**
- `client` - Django тестовый клиент
- `logged_in_client` - авторизованный клиент
- `api_client` - DRF API клиент
- `authenticated_api_client` - API клиент с JWT

**Контент:**
- `category` - категория
- `tag` - тег
- `post` - опубликованная статья
- `draft_post` - черновик
- `comment` - комментарий
- `subscription` - подписка

## 🔧 CI/CD

### GitHub Actions

Автоматический запуск при:
- Push в main/master/develop
- Создании pull request

**Проверяется:**
- ✅ Линтинг (flake8, black, isort)
- ✅ Тесты с покрытием (Python 3.10, 3.11, 3.12)
- ✅ Безопасность зависимостей (safety)
- ✅ Сборка Docker образа

## 📝 Написание тестов

### Пример теста модели
```python
@pytest.mark.django_db
@pytest.mark.unit
class TestUserModel:
    def test_user_follow(self, user, another_user):
        """Проверка подписки на пользователя"""
        user.follow(another_user)
        assert user.is_following(another_user)
        assert another_user in user.following.all()
```

### Пример теста view
```python
@pytest.mark.django_db
def test_profile_page(logged_in_client, user):
    """Проверка доступности страницы профиля"""
    url = reverse('users:profile')
    response = logged_in_client.get(url)
    assert response.status_code == 200
    assert user.username in response.content.decode()
```

### Пример теста API
```python
@pytest.mark.django_db
def test_like_post(authenticated_api_client, post):
    """Проверка лайка статьи через API"""
    url = reverse('api:post-like', kwargs={'pk': post.pk})
    response = authenticated_api_client.post(url)
    assert response.status_code == 200
    assert response.data['liked'] == True
```

## 🎯 Марки тестов

- `@pytest.mark.unit` - unit тесты
- `@pytest.mark.integration` - integration тесты
- `@pytest.mark.slow` - медленные тесты
- `@pytest.mark.django_db` - требует БД

## 📊 Отчет о покрытии

После запуска `run_tests.bat html` откройте `PageGlow/htmlcov/index.html`

## 🛠 Следующие шаги

### 1. Запустить тесты views
Некоторые тесты могут требовать доработки URL patterns.

### 2. Запустить тесты API
Требует настроенных API endpoints.

### 3. Добавить свои тесты
Следуйте существующим паттернам.

### 4. Настроить Codecov
Добавьте бейдж покрытия в README.

## 📚 Ресурсы

- [pytest documentation](https://docs.pytest.org/)
- [pytest-django](https://pytest-django.readthedocs.io/)
- [Factory Boy](https://factoryboy.readthedocs.io/)

## ❓ Troubleshooting

### Ошибка "Database access not allowed"
Добавьте `@pytest.mark.django_db` к тесту или классу.

### Ошибка импорта моделей
Проверьте что модели импортируются из правильных приложений.

### Тесты не находят фикстуры
Убедитесь что `conftest.py` в корне проекта.

---

**Создано:** 2026-03-15  
**Статус:** ✅ Model тесты работают (37/37)  
**Покрытие:** ~83%
