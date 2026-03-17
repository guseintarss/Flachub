"""
Утилиты для кэширования часто запрашиваемых данных
Помогает избежать излишних запросов к БД
"""

from django.core.cache import cache
from django.db.models import Count
from datetime import timedelta


class CacheKeys:
    """Ключи кэша"""
    AUTHOR_STATS = 'author_stats:{user_id}'
    POST_COMMENTS_COUNT = 'post_comments_count:{post_id}'
    POST_LIKES_COUNT = 'post_likes_count:{post_id}'
    POST_VIEWS = 'post_views:{post_id}'
    USER_POSTS_COUNT = 'user_posts_count:{user_id}'
    POPULAR_POSTS = 'popular_posts'
    SIDEBAR_CACHE = 'side_cache'


def get_author_stats(author_id, use_cache=True):
    """
    Получить статистику автора (подписчики, подписки)
    Используется кэширование на 1 час
    """
    cache_key = CacheKeys.AUTHOR_STATS.format(user_id=author_id)
    
    if use_cache:
        stats = cache.get(cache_key)
        if stats:
            return stats
    
    from main.models import Subscription
    
    # Подсчитываем подписчиков
    subscribers = Subscription.objects.filter(author_id=author_id).aggregate(
        count=Count('id')
    )['count']
    
    # Подсчитываем подписки
    subscriptions = Subscription.objects.filter(subscriber_id=author_id).aggregate(
        count=Count('id')
    )['count']
    
    stats = {
        'subscribers_count': subscribers,
        'subscriptions_count': subscriptions,
    }
    
    # Кэшируем на 1 час
    cache.set(cache_key, stats, 3600)
    return stats


def get_post_stats(post_id, use_cache=True):
    """
    Получить статистику поста (комментарии, лайки, просмотры)
    Используется кэширование на 10 минут для лайков/комментариев
    """
    from main.models import Post, Comment
    
    stats = {}
    
    # Комментарии
    comments_key = CacheKeys.POST_COMMENTS_COUNT.format(post_id=post_id)
    if use_cache:
        comments = cache.get(comments_key)
    else:
        comments = None
    
    if comments is None:
        comments = Comment.objects.filter(post_id=post_id, is_active=True).count()
        cache.set(comments_key, comments, 600)  # 10 минут
    
    stats['comments_count'] = comments
    
    # Лайки
    likes_key = CacheKeys.POST_LIKES_COUNT.format(post_id=post_id)
    if use_cache:
        likes = cache.get(likes_key)
    else:
        likes = None
    
    if likes is None:
        post = Post.objects.get(id=post_id)
        likes = post.likes.count()
        cache.set(likes_key, likes, 600)  # 10 минут
    
    stats['likes_count'] = likes
    
    # Просмотры из самого объекта
    try:
        post = Post.objects.get(id=post_id)
        stats['views'] = post.views
    except Post.DoesNotExist:
        stats['views'] = 0
    
    return stats


def invalidate_author_cache(author_id):
    """Очистить кэш статистики автора"""
    cache_key = CacheKeys.AUTHOR_STATS.format(user_id=author_id)
    cache.delete(cache_key)


def invalidate_post_cache(post_id):
    """Очистить кэш статистики поста"""
    cache.delete(CacheKeys.POST_COMMENTS_COUNT.format(post_id=post_id))
    cache.delete(CacheKeys.POST_LIKES_COUNT.format(post_id=post_id))
    cache.delete(CacheKeys.POST_VIEWS.format(post_id=post_id))


def get_popular_posts(limit=20, use_cache=True):
    """
    Получить популярные посты по просмотрам
    Используется кэширование на 1 час
    """
    cache_key = CacheKeys.POPULAR_POSTS
    
    if use_cache:
        posts = cache.get(cache_key)
        if posts:
            return posts
    
    from main.models import Post
    
    posts = Post.published.all().order_by('-views')[:limit]
    # Преобразуем в список для кэширования
    posts_list = list(posts.values('id', 'title', 'slug', 'views', 'author_id'))
    
    cache.set(cache_key, posts_list, 3600)  # 1 час
    return posts_list


def invalidate_popular_posts_cache():
    """Очистить кэш популярных постов"""
    cache.delete(CacheKeys.POPULAR_POSTS)


# Batch operations для оптимизации
def batch_get_author_stats(author_ids):
    """
    Получить статистику для нескольких авторов за раз
    Минимизирует количество кэш-запросов
    """
    from main.models import Subscription
    from django.db.models import Q
    
    stats_map = {}
    uncached_ids = []
    
    # Сначала получаем из кэша
    for author_id in author_ids:
        cache_key = CacheKeys.AUTHOR_STATS.format(user_id=author_id)
        stats = cache.get(cache_key)
        if stats:
            stats_map[author_id] = stats
        else:
            uncached_ids.append(author_id)
    
    # Если есть некэшированные - получаем из БД
    if uncached_ids:
        for author_id in uncached_ids:
            subscribers = Subscription.objects.filter(author_id=author_id).count()
            subscriptions = Subscription.objects.filter(subscriber_id=author_id).count()
            
            stats = {
                'subscribers_count': subscribers,
                'subscriptions_count': subscriptions,
            }
            
            stats_map[author_id] = stats
            cache_key = CacheKeys.AUTHOR_STATS.format(user_id=author_id)
            cache.set(cache_key, stats, 3600)
    
    return stats_map
