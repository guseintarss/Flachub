"""
Сигналы для автоматической выдачи достижений (бейджей) пользователям
"""
from django.db.models import Count, Q, Sum
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.core.cache import cache
from main.models import Post, Comment, Bookmark, UserBadge, UserAchievement, Notification
import logging

logger = logging.getLogger(__name__)


def check_and_award_badge(user, badge_key, badge_name, badge_description, badge_icon, badge_color, reason):
    """
    Проверка и выдача бейджа пользователю
    """
    # Проверяем, есть ли уже такой бейдж у пользователя
    if UserAchievement.objects.filter(user=user, badge__key=badge_key).exists():
        return False
    
    # Создаём или получаем бейдж
    badge, _ = UserBadge.objects.get_or_create(
        key=badge_key,
        defaults={
            'name': badge_name,
            'description': badge_description,
            'icon': badge_icon,
            'color': badge_color,
            'is_active': True
        }
    )
    
    # Выдаём бейдж пользователю
    achievement, created = UserAchievement.objects.get_or_create(
        user=user,
        badge=badge,
        defaults={'reason': reason}
    )
    
    if created:
        # Создаём уведомление в базе
        try:
            Notification.objects.create(
                recipient=user,
                sender=None,
                notification_type='achievement',
                post=None,
                message=f'🏆 Вы получили достижение: "{badge_name}"!'
            )
        except Exception as e:
            logger.error(f'Ошибка создания уведомления о бейдже: {e}')
        
        return True
    return False


# ===== СИГНАЛЫ ДЛЯ СТАТЕЙ =====

@receiver(post_save, sender=Post)
def check_first_post_badge(sender, instance, created, **kwargs):
    """Бейдж за первую опубликованную статью"""
    if created and instance.is_published:
        author = instance.author
        if author:
            # Проверяем количество опубликованных статей
            published_count = Post.objects.filter(author=author, is_published=True).count()
            if published_count == 1:
                check_and_award_badge(
                    user=author,
                    badge_key='first_post',
                    badge_name='Первые шаги',
                    badge_description='Опубликована первая статья',
                    badge_icon='🌱',
                    badge_color='#4caf50',
                    reason='Первая опубликованная статья'
                )


@receiver(post_save, sender=Post)
def check_author_badge(sender, instance, created, **kwargs):
    """Бейдж за 10 опубликованных статей"""
    if created and instance.is_published:
        author = instance.author
        if author:
            published_count = Post.objects.filter(author=author, is_published=True).count()
            if published_count == 10:
                check_and_award_badge(
                    user=author,
                    badge_key='author',
                    badge_name='Автор',
                    badge_description='Опубликовано 10 статей',
                    badge_icon='✍️',
                    badge_color='#2196f3',
                    reason='10 опубликованных статей'
                )


@receiver(post_save, sender=Post)
def check_expert_badge(sender, instance, created, **kwargs):
    """Бейдж за статью с 500 просмотрами"""
    if instance.is_published and instance.views >= 500:
        author = instance.author
        if author:
            # Проверяем, есть ли уже статья с 500+ просмотрами
            popular_posts = Post.objects.filter(author=author, views__gte=500).count()
            if popular_posts == 1:
                check_and_award_badge(
                    user=author,
                    badge_key='expert',
                    badge_name='Эксперт',
                    badge_description='Статья набрала 500+ просмотров',
                    badge_icon='🎓',
                    badge_color='#ff9800',
                    reason='Статья набрала 500 просмотров'
                )


@receiver(post_save, sender=Post)
def check_popular_author_badge(sender, instance, **kwargs):
    """Бейдж за 1000+ суммарных просмотров"""
    if instance.is_published:
        author = instance.author
        if author:
            # Считаем суммарные просмотры всех статей
            total = Post.objects.filter(
                author=author, is_published=True
            ).aggregate(total=Sum('views'))['total'] or 0
            
            if total >= 1000:
                check_and_award_badge(
                    user=author,
                    badge_key='popular_author',
                    badge_name='Популярный автор',
                    badge_description='1000+ суммарных просмотров статей',
                    badge_icon='⭐',
                    badge_color='#e91e63',
                    reason='1000+ просмотров статей'
                )


# ===== СИГНАЛЫ ДЛЯ КОММЕНТАРИЕВ =====

@receiver(post_save, sender=Comment)
def check_first_comment_badge(sender, instance, created, **kwargs):
    """Бейдж за первый комментарий"""
    if created:
        author = instance.author
        if author:
            comment_count = Comment.objects.filter(author=author).count()
            if comment_count == 1:
                check_and_award_badge(
                    user=author,
                    badge_key='first_comment',
                    badge_name='Голос',
                    badge_description='Оставлен первый комментарий',
                    badge_icon='💬',
                    badge_color='#00bcd4',
                    reason='Первый комментарий'
                )


@receiver(post_save, sender=Comment)
def check_commentator_badge(sender, instance, created, **kwargs):
    """Бейдж за 50 комментариев"""
    if created:
        author = instance.author
        if author:
            comment_count = Comment.objects.filter(author=author).count()
            if comment_count == 50:
                check_and_award_badge(
                    user=author,
                    badge_key='commentator',
                    badge_name='Комментатор',
                    badge_description='Оставлено 50 комментариев',
                    badge_icon='🗣️',
                    badge_color='#9c27b0',
                    reason='50 комментариев'
                )


# ===== СИГНАЛЫ ДЛЯ ЗАКЛАДОК =====

@receiver(post_save, sender=Bookmark)
def check_bookmark_badge(sender, instance, created, **kwargs):
    """Бейдж за 10 закладок (Коллекционер)"""
    if created:
        user = instance.user
        bookmark_count = Bookmark.objects.filter(user=user).count()
        
        if bookmark_count == 10:
            check_and_award_badge(
                user=user,
                badge_key='collector',
                badge_name='Коллекционер',
                badge_description='Собрано 10 закладок',
                badge_icon='📚',
                badge_color='#673ab7',
                reason='10 закладок'
            )
        
        elif bookmark_count == 50:
            check_and_award_badge(
                user=user,
                badge_key='super_collector',
                badge_name='Супер коллекционер',
                badge_description='Собрано 50 закладок',
                badge_icon='📖',
                badge_color='#3f51b5',
                reason='50 закладок'
            )


# ===== СИГНАЛЫ ДЛЯ ОБНОВЛЕНИЯ SIDEBAR =====

@receiver(post_delete, sender=Post)
@receiver(m2m_changed, sender=Post.tags.through)
def invalidate_sidebar_cache(sender, instance=None, **kwargs):
    """Инвалидация кэша sidebar при удалении поста или изменении связей"""
    cache.delete('sidebar_context_data')
    # Также инвалидируем кэш шаблонов
    from django.core.cache.utils import make_template_fragment_key
    cache.delete(make_template_fragment_key("side_cache"))


@receiver(post_save, sender='main.Category')
@receiver(post_delete, sender='main.Category')
def invalidate_sidebar_cache_on_category_change(sender, instance=None, **kwargs):
    """Инвалидация кэша sidebar при создании/удалении категории"""
    cache.delete('sidebar_context_data')
    from django.core.cache.utils import make_template_fragment_key
    cache.delete(make_template_fragment_key("side_cache"))
