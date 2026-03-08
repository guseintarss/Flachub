"""
Оптимизированные ORM запросы для основных операций
Использует select_related и prefetch_related для минимизации запросов
"""

from django.db.models import Q, Prefetch, Count
from main.models import Post, Comment, Subscription, Notification
from users.models import User


class OptimizedQueries:
    """Коллекция оптимизированных запросов к БД"""
    
    @staticmethod
    def get_posts_list(published_only=True, limit=None):
        """
        Получить список постов с оптимизацией
        Один запрос вместо 3+ запросов за пост
        """
        queryset = Post.objects.select_related(
            'author',
            'cat'
        ).prefetch_related(
            'tags',
            'likes',
            'favorites',
            Prefetch('comments', queryset=Comment.objects.filter(is_active=True))
        )
        
        if published_only:
            queryset = queryset.filter(is_published=Post.Status.PUBLISHED)
        
        if limit:
            queryset = queryset[:limit]
        
        return queryset
    
    @staticmethod
    def get_post_detail(post_slug):
        """Получить детали поста с максимальной оптимизацией"""
        return Post.objects.select_related(
            'author__freelancer_profile',
            'cat'
        ).prefetch_related(
            'tags',
            'likes',
            'favorites',
            Prefetch(
                'comments',
                queryset=Comment.objects.select_related('author').filter(is_active=True)
            )
        ).get(slug=post_slug)
    
    @staticmethod
    def get_user_profile_posts(user):
        """Получить все посты пользователя с оптимизацией"""
        return user.posts.select_related(
            'cat'
        ).prefetch_related('tags')
    
    @staticmethod
    def get_author_public_profile(author):
        """Получить информацию для публичного профиля автора"""
        # Оптимизируем запросы для подписок
        published_posts = author.posts.filter(
            is_published=Post.Status.PUBLISHED
        ).select_related('cat').prefetch_related('tags')
        
        subscribers_count = Subscription.objects.filter(author=author).count()
        subscriptions_count = Subscription.objects.filter(subscriber=author).count()
        
        return {
            'posts': published_posts,
            'subscribers_count': subscribers_count,
            'subscriptions_count': subscriptions_count,
        }
    
    @staticmethod
    def get_user_notifications(user, limit=20):
        """Получить уведомления пользователя с оптимизацией"""
        return Notification.objects.filter(
            recipient=user
        ).select_related(
            'sender',
            'post',
            'comment'
        ).order_by('-created_at')[:limit]
    
    @staticmethod
    def get_subscription_feed(user, limit=50):
        """
        Получить ленту постов от подписок
        Оптимизированный запрос без N+1 проблемы
        """
        subscribed_authors = Subscription.objects.filter(
            subscriber=user
        ).values_list('author_id', flat=True)
        
        return Post.published.filter(
            author_id__in=subscribed_authors
        ).select_related(
            'author',
            'cat'
        ).prefetch_related(
            'tags',
            'likes',
            'favorites'
        ).order_by('-time_create')[:limit]
    
    @staticmethod
    def get_comments_for_post(post, include_inactive=False):
        """Получить комментарии для поста с оптимизацией"""
        queryset = Comment.objects.filter(post=post).select_related('author')
        
        if not include_inactive:
            queryset = queryset.filter(is_active=True)
        
        return queryset.order_by('-created_at')
    
    @staticmethod
    def search_posts(query):
        """Оптимизированный поиск постов"""
        return Post.published.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        ).select_related(
            'author',
            'cat'
        ).prefetch_related('tags')
    
    @staticmethod
    def get_posts_by_category(category_slug):
        """Получить посты категории с оптимизацией"""
        return Post.published.filter(
            cat__slug=category_slug
        ).select_related('cat').prefetch_related('tags')
    
    @staticmethod
    def get_posts_by_tag(tag_slug):
        """Получить посты по тегу с оптимизацией"""
        return Post.published.filter(
            tags__slug=tag_slug
        ).select_related('cat').prefetch_related('tags')
    
    @staticmethod
    def get_popular_posts(limit=20):
        """Получить популярные посты с оптимизацией"""
        return Post.published.select_related(
            'author',
            'cat'
        ).prefetch_related('tags').order_by('-views')[:limit]


class BulkOperationOptimizer:
    """Оптимизация для массовых операций"""
    
    @staticmethod
    def bulk_get_post_stats(post_ids):
        """
        Получить статистику для нескольких постов за один запрос
        
        Args:
            post_ids: список ID постов
            
        Returns:
            dict: {post_id: {'likes': count, 'comments': count, ...}}
        """
        from django.db.models import Count
        
        # Используем annotation для подсчёта в одном запросе
        posts = Post.objects.filter(
            id__in=post_ids
        ).annotate(
            likes_count=Count('likes'),
            comments_count=Count('comments')
        ).values('id', 'views', 'likes_count', 'comments_count')
        
        stats_dict = {}
        for post in posts:
            stats_dict[post['id']] = {
                'likes': post['likes_count'],
                'comments': post['comments_count'],
                'views': post['views'],
            }
        
        return stats_dict
    
    @staticmethod
    def bulk_get_subscriptions(user_ids):
        """Получить информацию о подписках для нескольких пользователей"""
        subscriptions = Subscription.objects.filter(
            subscriber_id__in=user_ids
        ).values('subscriber_id', 'author_id').distinct()
        
        subs_dict = {}
        for user_id in user_ids:
            subs_dict[user_id] = [
                sub['author_id'] for sub in subscriptions 
                if sub['subscriber_id'] == user_id
            ]
        
        return subs_dict


# Декоратор для оптимизации запросов в views
def optimized_query(queryset_func):
    """
    Декоратор для автоматической оптимизации ORM запросов
    
    Использование:
    @optimized_query
    def get_posts(self):
        return Post.objects.all()
    """
    def wrapper(*args, **kwargs):
        queryset = queryset_func(*args, **kwargs)
        
        # Автоматически добавляем select_related и prefetch_related
        # в зависимости от типа queryset
        if hasattr(queryset, 'model'):
            if queryset.model.__name__ == 'Post':
                return queryset.select_related('author', 'cat').prefetch_related('tags')
            elif queryset.model.__name__ == 'Comment':
                return queryset.select_related('author', 'post')
            elif queryset.model.__name__ == 'Notification':
                return queryset.select_related('sender', 'post', 'comment')
        
        return queryset
    
    return wrapper
