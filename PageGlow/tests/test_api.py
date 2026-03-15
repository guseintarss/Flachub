"""
Тесты для API endpoints PageGlow
"""
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from users.models import Subscription

User = get_user_model()


# ===== AUTHENTICATION API TESTS =====

@pytest.mark.unit
class TestAuthAPI:
    """Тесты API аутентификации"""

    def test_user_registration(self, api_client):
        """Проверка регистрации пользователя"""
        url = reverse('user-list')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepass123'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_user_login(self, api_client, user):
        """Проверка входа через API"""
        url = reverse('jwt-create')
        data = {
            'username': user.username,
            'password': 'testpass123'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_user_login_invalid_credentials(self, api_client):
        """Проверка входа с неверными данными"""
        url = reverse('jwt-create')
        data = {
            'username': 'nonexistent',
            'password': 'wrongpass'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_refresh(self, api_client, user):
        """Проверка обновления токена"""
        # Получаем токены
        login_url = reverse('jwt-create')
        login_data = {'username': user.username, 'password': 'testpass123'}
        login_response = api_client.post(login_url, login_data)
        refresh_token = login_response.data['refresh']
        
        # Обновляем токен
        refresh_url = reverse('jwt-refresh')
        response = api_client.post(refresh_url, {'refresh': refresh_token})
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    def test_protected_endpoint_without_token(self, api_client):
        """Проверка защищенного эндпоинта без токена"""
        url = reverse('api:profile-me')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_protected_endpoint_with_token(self, authenticated_api_client):
        """Проверка защищенного эндпоинта с токеном"""
        url = reverse('api:profile-me')
        response = authenticated_api_client.get(url)
        assert response.status_code == status.HTTP_200_OK


# ===== USER PROFILE API TESTS =====

@pytest.mark.unit
class TestUserAPI:
    """Тесты API пользователей"""

    def test_get_user_profile(self, api_client, user):
        """Проверка получения профиля пользователя"""
        url = reverse('user-detail', kwargs={'pk': user.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == user.username

    def test_update_own_profile(self, authenticated_api_client):
        """Проверка обновления своего профиля"""
        url = reverse('api:profile-me')
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        response = authenticated_api_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'Updated'

    def test_get_current_user_profile(self, authenticated_api_client):
        """Проверка получения текущего пользователя"""
        url = reverse('api:profile-me')
        response = authenticated_api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'username' in response.data


# ===== SUBSCRIPTION API TESTS =====

@pytest.mark.unit
class TestSubscriptionAPI:
    """Тесты API подписок"""

    def test_get_subscriptions(self, authenticated_api_client, user, subscription):
        """Проверка получения списка подписок"""
        url = reverse('api:user-subscriptions', kwargs={'user_id': user.id})
        response = authenticated_api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_get_subscribers(self, authenticated_api_client, another_user, subscription):
        """Проверка получения списка подписчиков"""
        url = reverse('api:user-subscribers', kwargs={'user_id': another_user.id})
        response = authenticated_api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_create_subscription(self, authenticated_api_client, another_user):
        """Проверка создания подписки"""
        url = reverse('api:subscribe', kwargs={'user_id': another_user.id})
        response = authenticated_api_client.post(url)
        assert response.status_code == status.HTTP_201_CREATED

    def test_delete_subscription(self, authenticated_api_client, another_user, subscription):
        """Проверка удаления подписки"""
        url = reverse('api:subscribe', kwargs={'user_id': another_user.id})
        response = authenticated_api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_subscription_requires_auth(self, api_client, user):
        """Проверка что подписка требует авторизации"""
        url = reverse('api:subscribe', kwargs={'user_id': user.id})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ===== POST API TESTS =====

@pytest.mark.unit
class TestPostAPI:
    """Тесты API статей"""

    def test_list_posts(self, api_client, published_posts):
        """Проверка получения списка статей"""
        url = reverse('api:post-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0

    def test_get_post_detail(self, api_client, post):
        """Проверка получения детали статьи"""
        url = reverse('api:post-detail', kwargs={'pk': post.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == post.title

    def test_create_post(self, authenticated_api_client, category):
        """Проверка создания статьи"""
        url = reverse('api:post-list')
        data = {
            'title': 'API Post',
            'slug': 'api-post',
            'content': '<p>Content from API</p>',
            'cat': category.id,
            'is_published': True
        }
        response = authenticated_api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_update_own_post(self, authenticated_api_client, post):
        """Проверка обновления своей статьи"""
        url = reverse('api:post-detail', kwargs={'pk': post.pk})
        data = {'title': 'Updated Title'}
        response = authenticated_api_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Updated Title'

    def test_delete_own_post(self, authenticated_api_client, post):
        """Проверка удаления своей статьи"""
        url = reverse('api:post-detail', kwargs={'pk': post.pk})
        response = authenticated_api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_draft_not_public(self, api_client, draft_post):
        """Проверка что черновик не доступен публично"""
        url = reverse('api:post-detail', kwargs={'pk': draft_post.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ===== LIKE API TESTS =====

@pytest.mark.unit
class TestLikeAPI:
    """Тесты API лайков"""

    def test_like_post(self, authenticated_api_client, post):
        """Проверка лайка статьи через API"""
        url = reverse('api:post-like', kwargs={'pk': post.pk})
        response = authenticated_api_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['liked'] == True

    def test_unlike_post(self, authenticated_api_client, post):
        """Проверка удаления лайка через API"""
        # Сначала лайкаем
        authenticated_api_client.post(reverse('api:post-like', kwargs={'pk': post.pk}))
        
        # Затем убираем лайк
        url = reverse('api:post-like', kwargs={'pk': post.pk})
        response = authenticated_api_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['liked'] == False

    def test_like_requires_auth(self, api_client, post):
        """Проверка что лайк требует авторизации"""
        url = reverse('api:post-like', kwargs={'pk': post.pk})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ===== COMMENT API TESTS =====

@pytest.mark.unit
class TestCommentAPI:
    """Тесты API комментариев"""

    def test_list_comments(self, api_client, post, comment):
        """Проверка получения списка комментариев"""
        url = reverse('api:comment-list')
        response = api_client.get(url, {'post': post.pk})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0

    def test_create_comment(self, authenticated_api_client, post):
        """Проверка создания комментария"""
        url = reverse('api:comment-list')
        data = {
            'post': post.pk,
            'content': 'Comment from API'
        }
        response = authenticated_api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_delete_own_comment(self, authenticated_api_client, comment):
        """Проверка удаления своего комментария"""
        url = reverse('api:comment-detail', kwargs={'pk': comment.pk})
        response = authenticated_api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT


# ===== CATEGORY API TESTS =====

@pytest.mark.unit
class TestCategoryAPI:
    """Тесты API категорий"""

    def test_list_categories(self, api_client, category):
        """Проверка получения списка категорий"""
        url = reverse('api:category-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0

    def test_get_category_detail(self, api_client, category):
        """Проверка получения детали категории"""
        url = reverse('api:category-detail', kwargs={'pk': category.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == category.name


# ===== TAG API TESTS =====

@pytest.mark.unit
class TestTagAPI:
    """Тесты API тегов"""

    def test_list_tags(self, api_client, tag):
        """Проверка получения списка тегов"""
        url = reverse('api:tagpost-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0


# ===== NOTIFICATION API TESTS =====

@pytest.mark.unit
class TestNotificationAPI:
    """Тесты API уведомлений"""

    def test_list_notifications(self, authenticated_api_client, user):
        """Проверка получения списка уведомлений"""
        from users.models import Notification
        Notification.objects.create(
            recipient=user,
            notification_type=Notification.NotificationType.LIKE,
            message='Test notification'
        )
        url = reverse('api:notification-list')
        response = authenticated_api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0

    def test_mark_notification_read(self, authenticated_api_client, user):
        """Проверка отметки уведомления как прочитанного"""
        from users.models import Notification
        notification = Notification.objects.create(
            recipient=user,
            notification_type=Notification.NotificationType.LIKE,
            message='Test',
            is_read=False
        )
        url = reverse('api:notification-mark-read', kwargs={'pk': notification.pk})
        response = authenticated_api_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        
        notification.refresh_from_db()
        assert notification.is_read == True
