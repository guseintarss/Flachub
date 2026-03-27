from .models import Post, Category, Comment
from django.contrib.auth import get_user_model
from django.db.models import Count, Q

User = get_user_model()

def sidebar_context(request):
    # Кэшируем статистику
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

    return {
        'sidebar_new_posts': Post.objects.filter(
            is_published=True
        ).select_related('author', 'cat').annotate(
            likes_count=Count('likes', distinct=True)
        ).order_by('-time_create')[:5],
        'sidebar_categories': sidebar_categories,
        'total_posts': total_posts,
        'total_users': total_users,
        'total_comments': total_comments,
    }
