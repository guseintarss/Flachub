"""
Pytest фикстуры для тестирования PageGlow
"""
import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from main.models import Post, Category, TagPost, Comment, Subscription, Notification
from users.models import Rule

User = get_user_model()


# ===== FIXTURES FOR USER =====

@pytest.fixture
def user_factory():
    """Фабрика для создания пользователей"""
    def create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        **kwargs
    ):
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            **kwargs
        )
        return user
    return create_user


@pytest.fixture
def user(user_factory):
    """Стандартный пользователь для тестов"""
    return user_factory()


@pytest.fixture
def another_user(user_factory):
    """Другой пользователь для тестов"""
    return user_factory(
        username='anotheruser',
        email='another@example.com'
    )


@pytest.fixture
def admin_user(user_factory):
    """Пользователь с правами суперпользователя"""
    return user_factory(
        username='admin',
        email='admin@example.com',
        is_staff=True,
        is_superuser=True
    )


# ===== FIXTURES FOR API CLIENTS =====

@pytest.fixture
def api_client():
    """Стандартный API клиент"""
    return APIClient()


@pytest.fixture
def authenticated_api_client(user):
    """API клиент с аутентификацией через JWT"""
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


@pytest.fixture
def client():
    """Стандартный Django тестовый клиент"""
    return Client()


@pytest.fixture
def logged_in_client(user):
    """Django клиент с авторизованным пользователем"""
    client = Client()
    client.force_login(user)
    return client


# ===== FIXTURES FOR CONTENT =====

@pytest.fixture
def category():
    """Категория для тестов"""
    return Category.objects.create(
        name='Тестовая категория',
        slug='test-category'
    )


@pytest.fixture
def tag():
    """Тег для тестов"""
    return TagPost.objects.create(
        tag='Тестовый тег',
        slug='test-tag'
    )


@pytest.fixture
def post(user, category, tag):
    """Статья для тестов"""
    post = Post.objects.create(
        title='Тестовая статья',
        slug='test-post',
        content='<p>Тестовый контент статьи</p>',
        cat=category,
        author=user,
        is_published=Post.Status.PUBLISHED
    )
    post.tags.add(tag)
    return post


@pytest.fixture
def draft_post(user, category):
    """Черновик статьи для тестов"""
    return Post.objects.create(
        title='Черновик',
        slug='draft-post',
        content='<p>Черновик контента</p>',
        cat=category,
        author=user,
        is_published=Post.Status.DRAFT
    )


@pytest.fixture
def published_posts(user, category):
    """Несколько опубликованных статей"""
    posts = []
    for i in range(5):
        post = Post.objects.create(
            title=f'Статья {i}',
            slug=f'post-{i}',
            content=f'<p>Контент статьи {i}</p>',
            cat=category,
            author=user,
            is_published=Post.Status.PUBLISHED
        )
        posts.append(post)
    return posts


# ===== FIXTURES FOR COMMENTS =====

@pytest.fixture
def comment(user, post):
    """Комментарий к статье"""
    return Comment.objects.create(
        post=post,
        author=user,
        content='Тестовый комментарий'
    )


# ===== FIXTURES FOR SUBSCRIPTIONS =====

@pytest.fixture
def subscription(user, another_user):
    """Подписка пользователя на другого пользователя"""
    return Subscription.objects.create(
        subscriber=user,
        author=another_user
    )


# ===== FIXTURES FOR RULES =====

@pytest.fixture
def rule():
    """Правило для тестов"""
    return Rule.objects.create(
        key='test_rule',
        value='test_value',
        description='Тестовое правило',
        is_active=True
    )


# ===== HELPER FIXTURES =====

@pytest.fixture
def create_post():
    """Фабрика для создания статей"""
    def _create_post(
        title='Test Post',
        author=None,
        category=None,
        is_published=Post.Status.PUBLISHED,
        **kwargs
    ):
        if not category:
            category = Category.objects.create(
                name='Default Category',
                slug='default-category'
            )
        if not author:
            author = User.objects.create_user(
                username='post_author',
                password='pass123'
            )
        
        return Post.objects.create(
            title=title,
            slug=title.lower().replace(' ', '-'),
            content='<p>Test content</p>',
            cat=category,
            author=author,
            is_published=is_published,
            **kwargs
        )
    return _create_post


@pytest.fixture
def create_user():
    """Фабрика для создания пользователей (альтернативная)"""
    def _create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        **kwargs
    ):
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
            **kwargs
        )
    return _create_user
