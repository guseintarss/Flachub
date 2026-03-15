# Тестирование в PageGlow

## 📋 Обзор

В проекте настроено полноценное тестирование с использованием **pytest** и **pytest-django**.

## 🚀 Быстрый старт

### Запуск всех тестов
```bash
# Используя Makefile
make test

# Используя bash скрипт
./run_tests.sh

# Используя pytest напрямую
pytest
```

### Запуск с покрытием
```bash
make test-cov
```

## 📁 Структура тестов

```
PageGlow/
├── conftest.py              # Общие фикстуры
├── pytest.ini               # Конфигурация pytest
├── tests/
│   ├── __init__.py
│   ├── test_models.py       # Тесты моделей
│   ├── test_views.py        # Тесты представлений
│   └── test_api.py          # Тесты API
```

## 🔧 Фикстуры

### Пользователи
- `user` - стандартный пользователь
- `another_user` - другой пользователь
- `admin_user` - суперпользователь
- `user_factory` - фабрика пользователей

### Клиенты
- `client` - Django тестовый клиент
- `logged_in_client` - авторизованный клиент
- `api_client` - DRF API клиент
- `authenticated_api_client` - авторизованный API клиент (JWT)

### Контент
- `category` - категория
- `tag` - тег
- `post` - опубликованная статья
- `draft_post` - черновик
- `comment` - комментарий
- `subscription` - подписка

## 📝 Примеры тестов

### Тест модели
```python
def test_post_creation(user, category):
    post = Post.objects.create(
        title='Test',
        slug='test',
        content='<p>Content</p>',
        cat=category,
        author=user
    )
    assert post.title == 'Test'
```

### Тест view
```python
def test_profile_page(logged_in_client, user):
    url = reverse('users:profile')
    response = logged_in_client.get(url)
    assert response.status_code == 200
```

### Тест API
```python
def test_create_post(authenticated_api_client, category):
    url = reverse('api:post-list')
    data = {'title': 'API Post', 'cat': category.id}
    response = authenticated_api_client.post(url, data)
    assert response.status_code == 201
```

## 🎯 Марки тестов

- `@pytest.mark.unit` - unit тесты
- `@pytest.mark.integration` - integration тесты
- `@pytest.mark.slow` - медленные тесты

### Запуск по маркерам
```bash
# Только unit тесты
pytest -m unit

# Кроме медленных
pytest -m "not slow"
```

## 📊 Отчет о покрытии

После запуска `make test-cov` откройте `htmlcov/index.html` в браузере.

## 🔄 CI/CD

GitHub Actions автоматически запускает тесты при:
- Push в main/master/develop
- Создании pull request

Проверяются:
- ✅ Линтинг (flake8, black, isort)
- ✅ Тесты с покрытием
- ✅ Безопасность зависимостей (safety)
- ✅ Сборка Docker образа

## 🛠 Полезные команды

```bash
# Запустить конкретный файл
pytest tests/test_models.py -v

# Запустить один тест
pytest tests/test_models.py::TestUserModel::test_user_creation -v

# Запустить упавшие тесты
pytest --lf

# Запустить новые тесты
pytest --nf

# Режим наблюдения
pytest-watch
```

## 📚 Лучшие практики

1. **Используйте фикстуры** для создания тестовых данных
2. **Именуйте тесты** понятно: `test_<functionality>_<condition>_<expected>`
3. **Один тест = одна проверка** (избегайте множественных assert)
4. **Изолируйте тесты** - каждый тест должен работать независимо
5. **Используйте маркеры** для категоризации тестов

## 🔧 Настройка окружения

Для локального тестирования создайте `.env.test`:
```env
SECRET_KEY=test-secret-key
DEBUG=True
DATABASE_URL=sqlite:///test_db.sqlite3
REDIS_URL=redis://localhost:6379/1
```

## 📖 Дополнительная литература

- [pytest documentation](https://docs.pytest.org/)
- [pytest-django](https://pytest-django.readthedocs.io/)
- [Factory Boy](https://factoryboy.readthedocs.io/)
