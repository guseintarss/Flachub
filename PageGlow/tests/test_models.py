"""
Тесты для моделей PageGlow
"""
import pytest
from django.contrib.auth import get_user_model

from main.models import Post, Category, TagPost, Comment, Subscription, Notification
from users.models import Rule

User = get_user_model()


# ===== USER MODEL TESTS =====

@pytest.mark.django_db
@pytest.mark.unit
class TestUserModel:
    """Тесты модели пользователя"""

    def test_user_creation(self, user_factory):
        """Проверка создания пользователя"""
        user = user_factory(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.first_name == 'Test'
        assert user.last_name == 'User'
        assert user.check_password('testpass123')

    def test_user_str_representation(self, user):
        """Проверка строкового представления"""
        assert str(user) == user.username

    def test_user_follow(self, user, another_user):
        """Проверка подписки на пользователя"""
        user.follow(another_user)
        assert user.is_following(another_user)
        assert another_user in user.following.all()

    def test_user_unfollow(self, user, another_user):
        """Проверка отписки от пользователя"""
        user.follow(another_user)
        user.unfollow(another_user)
        assert not user.is_following(another_user)
        assert another_user not in user.following.all()

    def test_user_cannot_follow_self(self, user):
        """Проверка что нельзя подписаться на себя"""
        initial_following_count = user.following.count()
        user.follow(user)
        assert user.following.count() == initial_following_count

    def test_user_get_followers_count(self, user, another_user):
        """Проверка подсчета подписчиков"""
        another_user.follow(user)
        assert user.get_followers_count() == 1

    def test_user_get_following_count(self, user, another_user):
        """Проверка подсчета подписок"""
        user.follow(another_user)
        assert user.get_following_count() == 1

    def test_user_is_subscribed_to(self, user, another_user):
        """Проверка статуса подписки"""
        user.follow(another_user)
        assert user.is_subscribed_to(another_user)

    def test_user_deprecated_methods(self, user, another_user):
        """Проверка обратной совместимости методов"""
        # Проверяем что deprecated методы работают
        user.subscribe_to(another_user)
        assert user.is_subscribed_to(another_user)
        
        user.unsubscribe_from(another_user)
        assert not user.is_subscribed_to(another_user)


# ===== POST MODEL TESTS =====

@pytest.mark.django_db
@pytest.mark.unit
class TestPostModel:
    """Тесты модели статьи"""

    def test_post_creation(self, user, category, post):
        """Проверка создания статьи"""
        assert post.title == 'Тестовая статья'
        assert post.author == user
        assert post.cat == category
        assert post.is_published == Post.Status.PUBLISHED

    def test_post_str_representation(self, post):
        """Проверка строкового представления"""
        assert str(post) == post.title

    def test_post_slug_generation(self, user, category):
        """Проверка автоматической генерации slug"""
        post = Post.objects.create(
            title='Статья с длинным названием',
            content='<p>Тест</p>',
            cat=category,
            author=user
        )
        assert post.slug == 'statya-s-dlinnym-nazvaniem'

    def test_post_number_of_likes(self, post, user, another_user):
        """Проверка подсчета лайков"""
        post.likes.add(user, another_user)
        assert post.number_of_likes() == 2

    def test_post_number_of_favorites(self, post, user, another_user):
        """Проверка подсчета избранных"""
        post.favorites.add(user, another_user)
        assert post.number_of_favorites() == 2

    def test_post_reading_time(self, user, category):
        """Проверка расчета времени чтения"""
        short_content = '<p>Короткая статья</p>'
        long_content = '<p>' + 'Слово ' * 400 + '</p>'
        
        short_post = Post.objects.create(
            title='Short',
            slug='short',
            content=short_content,
            cat=category,
            author=user
        )
        long_post = Post.objects.create(
            title='Long',
            slug='long',
            content=long_content,
            cat=category,
            author=user
        )
        
        assert short_post.reading_time() == 1
        assert long_post.reading_time() == 2

    def test_post_get_similar_posts(self, user, category, tag, post):
        """Проверка получения похожих статей"""
        similar_post = Post.objects.create(
            title='Похожая статья',
            slug='similar-post',
            content='<p>Контент</p>',
            cat=category,
            author=user,
            is_published=Post.Status.PUBLISHED
        )
        similar_post.tags.add(tag)
        
        similar = post.get_similar_posts()
        assert similar_post in similar

    def test_post_get_absolute_url(self, post):
        """Проверка получения URL статьи"""
        url = post.get_absolute_url()
        assert url == f'/post/{post.slug}/'

    def test_published_manager(self, user, category, draft_post):
        """Проверка менеджера опубликованных статей"""
        published = Post.published.all()
        drafts = Post.objects.filter(is_published=Post.Status.DRAFT)
        
        assert draft_post not in published
        assert draft_post in drafts

    def test_post_indexing(self, post):
        """Проверка что индексы работают"""
        # Просто проверяем что поля индексируются
        assert Post.objects.filter(slug=post.slug).exists()
        assert Post.objects.filter(cat=post.cat).exists()


# ===== CATEGORY MODEL TESTS =====

@pytest.mark.django_db
@pytest.mark.unit
class TestCategoryModel:
    """Тесты модели категории"""

    def test_category_creation(self):
        """Проверка создания категории"""
        category = Category.objects.create(
            name='Новая категория',
            slug='novaya-kategoriya'
        )
        assert category.name == 'Новая категория'
        assert category.slug == 'novaya-kategoriya'

    def test_category_str_representation(self, category):
        """Проверка строкового представления"""
        assert str(category) == category.name

    def test_category_slug_generation(self):
        """Проверка автоматической генерации slug"""
        category = Category.objects.create(
            name='Категория с кириллицей'
        )
        assert category.slug == 'kategoriya-s-kirillice'

    def test_category_get_absolute_url(self, category):
        """Проверка получения URL категории"""
        url = category.get_absolute_url()
        assert url == f'/category/{category.slug}/'


# ===== TAG MODEL TESTS =====

@pytest.mark.django_db
@pytest.mark.unit
class TestTagModel:
    """Тесты модели тега"""

    def test_tag_creation(self, tag):
        """Проверка создания тега"""
        assert tag.tag == 'Тестовый тег'
        assert tag.slug == 'test-tag'

    def test_tag_str_representation(self, tag):
        """Проверка строкового представления"""
        assert str(tag) == tag.tag

    def test_tag_get_absolute_url(self, tag):
        """Проверка получения URL тега"""
        url = tag.get_absolute_url()
        assert url == f'/tag/{tag.slug}/'


# ===== COMMENT MODEL TESTS =====

@pytest.mark.django_db
@pytest.mark.unit
class TestCommentModel:
    """Тесты модели комментария"""

    def test_comment_creation(self, comment):
        """Проверка создания комментария"""
        assert comment.content == 'Тестовый комментарий'
        assert comment.is_active == True

    def test_comment_str_representation(self, comment):
        """Проверка строкового представления"""
        assert str(comment) == f'Comment by {comment.author} on {comment.post}'

    def test_comment_ordering(self, user, post):
        """Проверка сортировки комментариев"""
        comment1 = Comment.objects.create(
            post=post,
            author=user,
            content='Первый комментарий'
        )
        comment2 = Comment.objects.create(
            post=post,
            author=user,
            content='Второй комментарий'
        )
        
        comments = Comment.objects.filter(post=post)
        assert list(comments) == [comment2, comment1]  # Новые первыми


# ===== SUBSCRIPTION MODEL TESTS =====

@pytest.mark.django_db
@pytest.mark.unit
class TestSubscriptionModel:
    """Тесты модели подписки"""

    def test_subscription_creation(self, user, another_user):
        """Проверка создания подписки"""
        subscription = Subscription.objects.create(
            subscriber=user,
            author=another_user
        )
        assert subscription.subscriber == user
        assert subscription.author == another_user

    def test_subscription_str_representation(self, subscription):
        """Проверка строкового представления"""
        expected = f'{subscription.subscriber} подписан на {subscription.author}'
        assert str(subscription) == expected

    def test_subscription_unique_constraint(self, user, another_user):
        """Проверка уникальности подписки"""
        Subscription.objects.create(
            subscriber=user,
            author=another_user
        )
        
        with pytest.raises(Exception):
            Subscription.objects.create(
                subscriber=user,
                author=another_user
            )


# ===== NOTIFICATION MODEL TESTS =====

@pytest.mark.django_db
@pytest.mark.unit
class TestNotificationModel:
    """Тесты модели уведомлений"""

    def test_notification_creation(self, user, another_user, post):
        """Проверка создания уведомления"""
        notification = Notification.objects.create(
            recipient=user,
            sender=another_user,
            notification_type=Notification.NotificationType.LIKE,
            post=post,
            message='Понравилось вашу статью'
        )
        assert notification.recipient == user
        assert notification.is_read == False

    def test_notification_str_representation(self, user, another_user):
        """Проверка строкового представления"""
        notification = Notification.objects.create(
            recipient=user,
            sender=another_user,
            notification_type=Notification.NotificationType.FOLLOW,
            message='Подписался на вас'
        )
        assert 'follow' in str(notification).lower()

    def test_notification_ordering(self, user, another_user):
        """Проверка сортировки уведомлений"""
        notif1 = Notification.objects.create(
            recipient=user,
            sender=another_user,
            notification_type=Notification.NotificationType.LIKE,
            message='Первое'
        )
        notif2 = Notification.objects.create(
            recipient=user,
            sender=another_user,
            notification_type=Notification.NotificationType.LIKE,
            message='Второе'
        )
        
        notifications = Notification.objects.filter(recipient=user)
        assert list(notifications) == [notif2, notif1]  # Новые первыми


# ===== RULE MODEL TESTS =====

@pytest.mark.django_db
@pytest.mark.unit
class TestRuleModel:
    """Тесты модели правил"""

    def test_rule_creation(self, rule):
        """Проверка создания правила"""
        assert rule.key == 'test_rule'
        assert rule.value == 'test_value'
        assert rule.is_active == True

    def test_rule_str_representation(self, rule):
        """Проверка строкового представления"""
        assert str(rule) == rule.key
