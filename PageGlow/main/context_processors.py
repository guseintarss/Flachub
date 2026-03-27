from .models import Post, Category, Comment
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.core.cache import cache

User = get_user_model()

def sidebar_context(request):
    # Кэшируем статистику
    cache_key = 'sidebar_context_data'
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    total_posts = Post.objects.count()
    total_users = User.objects.filter(is_active=True).count()
    total_comments = Comment.objects.count()

    # Категории с количеством постов
    sidebar_categories = Category.objects.annotate(
        posts_count=Count(
            'posts',
            filter=Q(posts__is_published=True)
        )
    ).filter(posts_count__gt=0).order_by('-posts_count')[:10]

    # Новые посты с оптимизацией
    sidebar_new_posts = list(
        Post.objects.filter(
            is_published=True
        ).select_related('author', 'cat').annotate(
            likes_count=Count('likes', distinct=True)
        ).order_by('-time_create')[:5]
    )

    result = {
        'sidebar_new_posts': sidebar_new_posts,
        'sidebar_categories': sidebar_categories,
        'total_posts': total_posts,
        'total_users': total_users,
        'total_comments': total_comments,
    }
    
    cache.set(cache_key, result, 300)  # Кэш на 5 минут
    return result
