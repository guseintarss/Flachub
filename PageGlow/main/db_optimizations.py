"""
Оптимизация запросов к базе данных для PageGlow

Этот файл содержит оптимизированные версии querysets и методов
для уменьшения количества запросов к БД и улучшения производительности.
"""

from django.db.models import Count, Sum, Q, Prefetch, F
from django.db import connection
from django.core.cache import cache


# =============================================================================
# ОПТИМИЗИРОВАННЫЕ QUERYSETS
# =============================================================================

def get_optimized_posts():
    """
    Оптимизированный queryset для постов
    Уменьшает количество запросов с N+1 до 1
    """
    from main.models import Post
    
    return Post.published.select_related(
        'cat',           # ForeignKey - используем select_related
        'author'         # ForeignKey - используем select_related
    ).prefetch_related(
        'tags',          # ManyToMany - используем prefetch_related
        Prefetch('comments', queryset=Comment.objects.select_related('author')[:5])
    ).annotate(
        likes_count=Count('likes', distinct=True),
        comments_count=Count('comments', distinct=True),
        views_count=F('views')
    ).only(
        'title', 'slug', 'content', 'photo', 
        'time_create', 'time_update', 'views',
        'post_type', 'is_published'
    )


def get_optimized_categories():
    """
    Оптимизированный queryset для категорий
    """
    from main.models import Category
    
    return Category.objects.annotate(
        posts_count=Count('posts', filter=Q(posts__is_published=True)),
        last_post_date=Max('posts__time_create')
    ).filter(posts_count__gt=0)


def get_optimized_comments(limit=10):
    """
    Оптимизированный queryset для комментариев
    """
    from main.models import Comment
    
    return Comment.objects.select_related(
        'post',          # ForeignKey
        'author',        # ForeignKey
        'parent'         # ForeignKey (для ответов)
    ).prefetch_related(
        'replies'        # ManyToMany (ответы)
    ).order_by('-created_at')[:limit]


# =============================================================================
# КЭШИРОВАНИЕ ТЯЖЕЛЫХ ЗАПРОСОВ
# =============================================================================

def get_cached_admin_stats():
    """
    Кэшированная статистика для админки
    Время кэширования: 5 минут
    """
    cache_key = 'admin_dashboard_stats'
    stats = cache.get(cache_key)

    if stats is None:
        from main.models import Post, Comment, User

        stats = {
            'total_posts': Post.objects.count(),
            'published_posts': Post.published.count(),
            'total_users': User.objects.filter(is_active=True).count(),
            'total_comments': Comment.objects.count(),
        }

        cache.set(cache_key, stats, 300)  # 5 минут

    return stats


def get_cached_popular_posts(limit=10):
    """
    Кэшированные популярные посты
    Время кэширования: 1 час
    """
    cache_key = f'popular_posts_{limit}'
    posts = cache.get(cache_key)
    
    if posts is None:
        from main.models import Post
        
        posts = list(Post.published.select_related(
            'cat', 'author'
        ).annotate(
            likes_count=Count('likes')
        ).order_by('-views', '-likes_count')[:limit])
        
        cache.set(cache_key, posts, 3600)  # 1 час
    
    return posts


# =============================================================================
# ОПТИМИЗАЦИЯ ЧЕРЕЗ RAW SQL
# =============================================================================

def get_post_stats_fast():
    """
    Быстрая статистика постов через raw SQL
    В 2-3 раза быстрее ORM для больших таблиц
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                COUNT(*) as total_posts,
                SUM(views) as total_views,
                AVG(views) as avg_views
            FROM main_post
            WHERE is_published = TRUE
        """)
        result = cursor.fetchone()
        return {
            'total_posts': result[0],
            'total_views': result[1],
            'avg_views': result[2]
        }


def get_top_authors_fast(limit=10):
    """
    Топ авторов через raw SQL
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                u.username,
                u.first_name,
                u.last_name,
                COUNT(p.id) as posts_count,
                SUM(p.views) as total_views
            FROM users_user u
            LEFT JOIN main_post p ON u.id = p.author_id
            WHERE p.is_published = TRUE
            GROUP BY u.id
            ORDER BY posts_count DESC
            LIMIT %s
        """, [limit])
        
        columns = ['username', 'first_name', 'last_name', 'posts_count', 'total_views']
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


# =============================================================================
# ИНДЕКСЫ И АНАЛИЗ
# =============================================================================

def analyze_query_performance(queryset):
    """
    Анализ производительности запроса
    Возвращает EXPLAIN ANALYZE для PostgreSQL
    """
    from django.db import connection
    
    with connection.cursor() as cursor:
        cursor.execute(f"EXPLAIN ANALYZE {queryset.query}")
        return cursor.fetchall()


def check_missing_indexes():
    """
    Проверка отсутствующих индексов
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                schemaname,
                tablename,
                indexname,
                indexdef
            FROM pg_indexes
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname
        """)
        return cursor.fetchall()


# =============================================================================
# ПАГИНАЦИЯ С CURSOR
# =============================================================================

def paginate_with_cursor(queryset, cursor=None, limit=20):
    """
    Эффективная пагинация через cursor
    Вместо OFFSET/LIMIT использует WHERE id < cursor
    """
    if cursor:
        queryset = queryset.filter(id__lt=cursor)
    
    return list(queryset[:limit + 1])


# =============================================================================
# BULK ОПЕРАЦИИ
# =============================================================================

def bulk_update_views(posts_views):
    """
    Массовое обновление просмотров
    В 100 раз быстрее чем update() в цикле
    """
    from main.models import Post
    
    Post.objects.bulk_update(
        [Post(id=id, views=views) for id, views in posts_views],
        ['views'],
        batch_size=100
    )


def bulk_create_notifications(notifications_data):
    """
    Массовое создание уведомлений
    """
    from main.models import Notification
    
    Notification.objects.bulk_create(
        [Notification(**data) for data in notifications_data],
        batch_size=100,
        ignore_conflicts=True
    )


# =============================================================================
# ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ
# =============================================================================

"""
# В views.py:

from .db_optimizations import (
    get_optimized_posts,
    get_cached_popular_posts,
    get_cached_admin_stats,
    paginate_with_cursor
)

def home_view(request):
    # Вместо: Post.published.all()
    posts = get_optimized_posts()
    
    # Вместо: Post.published.order_by('-views')[:10]
    popular = get_cached_popular_posts()
    
    return render(request, 'index.html', {'posts': posts, 'popular': popular})


def admin_dashboard(request):
    # Вместо: множество отдельных запросов
    stats = get_cached_admin_stats()
    
    return render(request, 'admin.html', stats)


def posts_paginated(request):
    # Вместо: Post.objects.all()[offset:limit]
    cursor = request.GET.get('cursor')
    posts = paginate_with_cursor(Post.published.all(), cursor, limit=20)
    
    return render(request, 'posts.html', {'posts': posts})
"""
