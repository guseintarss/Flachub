from django.contrib.sitemaps import Sitemap
from django.utils import timezone
from main.models import Post, Category, TagPost
from users.models import User
from datetime import timedelta


class StaticViewSitemap(Sitemap):
    """Карта статических страниц SPA."""

    def items(self):
        return [
            {'location': '/', 'priority': 1.0, 'changefreq': 'daily'},
            {'location': '/search/', 'priority': 0.5, 'changefreq': 'daily'},
        ]

    def location(self, item):
        return item['location']

    def priority(self, item):
        return item['priority']

    def changefreq(self, item):
        return item['changefreq']


class PostSitemap(Sitemap):
    """Карта статей"""
    changefreq = "weekly"

    def items(self):
        return Post.published.select_related('cat', 'author').prefetch_related('tags')

    def lastmod(self, obj):
        return obj.time_update

    def priority(self, obj):
        # Популярные статьи имеют высший приоритет
        if obj.views > 1000:
            return 1.0
        elif obj.views > 500:
            return 0.9
        elif obj.views > 100:
            return 0.8
        return 0.7


class CategorySitemap(Sitemap):
    """Карта категорий"""
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Category.objects.order_by('pk')

    def lastmod(self, obj):
        # Дата последнего поста в категории
        last_post = obj.posts.filter(is_published=True).order_by('-time_update').first()
        return last_post.time_update if last_post else timezone.now()


class TagSitemap(Sitemap):
    """Карта тегов"""
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return TagPost.objects.order_by('pk')

    def lastmod(self, obj):
        # Дата последнего поста с тегом
        last_post = obj.tags.filter(is_published=True).order_by('-time_update').first()
        return last_post.time_update if last_post else timezone.now()


class UserSitemap(Sitemap):
    """Карта профилей пользователей"""
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return User.objects.filter(is_active=True).order_by('pk')

    def location(self, obj):
        return f'/user/{obj.username}/'

    def lastmod(self, obj):
        return obj.updated_at
