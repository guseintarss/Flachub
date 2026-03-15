"""
Тесты для views (представлений) PageGlow
"""
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

from main.models import Post, Category

User = get_user_model()


# ===== PROFILE VIEWS TESTS =====

@pytest.mark.unit
class TestProfileViews:
    """Тесты представлений профиля"""

    def test_profile_page_accessible(self, logged_in_client, user):
        """Проверка доступности страницы профиля"""
        url = reverse('users:profile')
        response = logged_in_client.get(url)
        assert response.status_code == 200
        assert user.username in response.content.decode()

    def test_profile_requires_login(self, client):
        """Проверка что профиль требует авторизации"""
        url = reverse('users:profile')
        response = client.get(url)
        assert response.status_code == 302  # Redirect to login

    def test_author_profile_page(self, client, user, post):
        """Проверка страницы профиля автора"""
        url = reverse('users:author_profile', kwargs={'username': user.username})
        response = client.get(url)
        assert response.status_code == 200
        assert user.username in response.content.decode()

    def test_author_profile_shows_posts(self, client, user, post):
        """Проверка что статьи автора отображаются"""
        url = reverse('users:author_profile', kwargs={'username': user.username})
        response = client.get(url)
        assert post.title in response.content.decode()

    def test_draft_not_visible_to_others(self, client, user, draft_post):
        """Проверка что черновики не видны другим"""
        url = reverse('users:author_profile', kwargs={'username': user.username})
        response = client.get(url)
        assert draft_post.title not in response.content.decode()


# ===== SUBSCRIPTION VIEWS TESTS =====

@pytest.mark.unit
class TestSubscriptionViews:
    """Тесты представлений подписок"""

    def test_subscribe_to_author(self, logged_in_client, another_user):
        """Проверка подписки на автора"""
        url = reverse('subscribe_author')
        response = logged_in_client.post(url, {'author_id': another_user.id})
        assert response.status_code == 200
        
        data = response.json()
        assert data['success'] == True
        assert data['subscribed'] == True

    def test_unsubscribe_from_author(self, logged_in_client, another_user, subscription):
        """Проверка отписки от автора"""
        url = reverse('subscribe_author')
        response = logged_in_client.post(url, {'author_id': another_user.id})
        assert response.status_code == 200
        
        data = response.json()
        assert data['success'] == True
        assert data['subscribed'] == False

    def test_subscribe_requires_login(self, client, user):
        """Проверка что подписка требует авторизации"""
        url = reverse('subscribe_author')
        response = client.post(url, {'author_id': user.id})
        assert response.status_code == 302

    def test_cannot_subscribe_to_self(self, logged_in_client, user):
        """Проверка что нельзя подписаться на себя"""
        url = reverse('subscribe_author')
        response = logged_in_client.post(url, {'author_id': user.id})
        assert response.status_code == 200
        
        data = response.json()
        assert data['success'] == False

    def test_subscriptions_widget(self, logged_in_client, user, subscription):
        """Проверка виджета подписок"""
        url = reverse('users:subscriptions_widget')
        response = logged_in_client.get(url)
        assert response.status_code == 200


# ===== POST VIEWS TESTS =====

@pytest.mark.unit
class TestPostViews:
    """Тесты представлений статей"""

    def test_post_detail_page(self, client, post):
        """Проверка страницы статьи"""
        url = reverse('post', kwargs={'post_slug': post.slug})
        response = client.get(url)
        assert response.status_code == 200
        assert post.title in response.content.decode()

    def test_post_detail_increases_views(self, client, post):
        """Проверка что просмотр увеличивает счетчик"""
        url = reverse('post', kwargs={'post_slug': post.slug})
        initial_views = post.views
        client.get(url)
        post.refresh_from_db()
        assert post.views > initial_views

    def test_draft_not_accessible_to_others(self, client, user, draft_post):
        """Проверка что черновик не доступен другим"""
        url = reverse('post', kwargs={'post_slug': draft_post.slug})
        response = client.get(url)
        assert response.status_code == 404

    def test_draft_accessible_to_author(self, logged_in_client, draft_post):
        """Проверка что черновик доступен автору"""
        url = reverse('edit_page', kwargs={'slug': draft_post.slug})
        response = logged_in_client.get(url)
        assert response.status_code == 200

    def test_category_filter(self, client, category, post):
        """Проверка фильтрации по категории"""
        url = reverse('category', kwargs={'cat_slug': category.slug})
        response = client.get(url)
        assert response.status_code == 200
        assert post.title in response.content.decode()

    def test_tag_filter(self, client, tag, post):
        """Проверка фильтрации по тегу"""
        url = reverse('tag', kwargs={'tag_slug': tag.slug})
        response = client.get(url)
        assert response.status_code == 200
        assert post.title in response.content.decode()


# ===== COMMENT VIEWS TESTS =====

@pytest.mark.unit
class TestCommentViews:
    """Тесты представлений комментариев"""

    def test_add_comment(self, logged_in_client, post):
        """Проверка добавления комментария"""
        url = reverse('add_comment', kwargs={'post_id': post.id})
        response = logged_in_client.post(url, {
            'content': 'Новый комментарий'
        })
        assert response.status_code == 302  # Redirect after success

    def test_add_comment_requires_login(self, client, post):
        """Проверка что комментарий требует авторизации"""
        url = reverse('add_comment', kwargs={'post_id': post.id})
        response = client.post(url, {'content': 'Комментарий'})
        assert response.status_code == 302

    def test_delete_comment(self, logged_in_client, comment):
        """Проверка удаления комментария"""
        url = reverse('delete_comment', kwargs={'comment_id': comment.id})
        response = logged_in_client.get(url)
        assert response.status_code == 302


# ===== LIKE VIEWS TESTS =====

@pytest.mark.unit
class TestLikeViews:
    """Тесты представлений лайков"""

    def test_like_post(self, logged_in_client, post):
        """Проверка лайка статьи"""
        url = reverse('like_post', kwargs={'post_id': post.id})
        response = logged_in_client.post(url)
        assert response.status_code == 200
        
        data = response.json()
        assert data['liked'] == True

    def test_unlike_post(self, logged_in_client, post):
        """Проверка удаления лайка"""
        # Сначала лайкаем
        logged_in_client.post(reverse('like_post', kwargs={'post_id': post.id}))
        
        # Затем убираем лайк
        url = reverse('like_post', kwargs={'post_id': post.id})
        response = logged_in_client.post(url)
        assert response.status_code == 200
        
        data = response.json()
        assert data['liked'] == False

    def test_like_requires_login(self, client, post):
        """Проверка что лайк требует авторизации"""
        url = reverse('like_post', kwargs={'post_id': post.id})
        response = client.post(url)
        assert response.status_code == 302


# ===== FAVORITE VIEWS TESTS =====

@pytest.mark.unit
class TestFavoriteViews:
    """Тесты представлений избранных"""

    def test_add_to_favorites(self, logged_in_client, post):
        """Проверка добавления в избранное"""
        url = reverse('add_to_favorites', kwargs={'post_id': post.id})
        response = logged_in_client.post(url)
        assert response.status_code == 200

    def test_remove_from_favorites(self, logged_in_client, post):
        """Проверка удаления из избранного"""
        # Сначала добавляем
        logged_in_client.post(reverse('add_to_favorites', kwargs={'post_id': post.id}))
        
        # Затем убираем
        url = reverse('add_to_favorites', kwargs={'post_id': post.id})
        response = logged_in_client.post(url)
        assert response.status_code == 200

    def test_favorites_page(self, logged_in_client, user, post):
        """Проверка страницы избранного"""
        user.favorited_posts.add(post)
        url = reverse('users:favorites')
        response = logged_in_client.get(url)
        assert response.status_code == 200
        assert post.title in response.content.decode()


# ===== SEARCH VIEWS TESTS =====

@pytest.mark.unit
class TestSearchViews:
    """Тесты представлений поиска"""

    def test_search_results(self, client, post):
        """Проверка поиска статей"""
        url = reverse('search')
        response = client.get(url, {'q': post.title})
        assert response.status_code == 200
        assert post.title in response.content.decode()

    def test_search_no_results(self, client):
        """Проверка поиска без результатов"""
        url = reverse('search')
        response = client.get(url, {'q': 'несуществующий запрос'})
        assert response.status_code == 200


# ===== DISCUSSION VIEWS TESTS =====

@pytest.mark.unit
class TestDiscussionViews:
    """Тесты представлений обсуждений"""

    def test_discussions_list(self, client):
        """Проверка списка обсуждений"""
        url = reverse('discussions')
        response = client.get(url)
        assert response.status_code == 200

    def test_create_discussion_requires_login(self, client):
        """Проверка что создание требует авторизации"""
        url = reverse('create_discussion')
        response = client.get(url)
        assert response.status_code == 302

    def test_discussion_detail(self, client, discussion):
        """Проверка страницы обсуждения"""
        url = reverse('discussion_detail', kwargs={'pk': discussion.pk})
        response = client.get(url)
        assert response.status_code == 200
        assert discussion.title in response.content.decode()


# ===== NOTIFICATION VIEWS TESTS =====

@pytest.mark.unit
class TestNotificationViews:
    """Тесты представлений уведомлений"""

    def test_notifications_list(self, logged_in_client, user):
        """Проверка списка уведомлений"""
        url = reverse('notifications')
        response = logged_in_client.get(url)
        assert response.status_code == 200

    def test_mark_notification_as_read(self, logged_in_client, user):
        """Проверка отметки уведомления как прочитанного"""
        from users.models import Notification
        notification = Notification.objects.create(
            recipient=user,
            notification_type=Notification.NotificationType.LIKE,
            message='Тест'
        )
        url = reverse('mark_notification_read', kwargs={'notification_id': notification.id})
        response = logged_in_client.get(url)
        assert response.status_code == 302
        
        notification.refresh_from_db()
        assert notification.is_read == True
