"""
RSS/Atom feeds for PageGlow
"""
from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils import feedgenerator
from django.utils.encoding import force_str
from django.utils.html import strip_tags
from bs4 import BeautifulSoup
from main.models import Post
import re


class LatestPostsFeed(Feed):
    """RSS лента последних статей"""
    title = "PageGlow - Последние статьи"
    link = "/"
    description = "Последние опубликованные статьи на PageGlow"
    description_template = "feeds/posts_description.html"

    def items(self):
        return Post.published.select_related('author', 'cat').order_by('-time_create')[:30]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        # Очищаем HTML от лишних тегов
        soup = BeautifulSoup(item.content, 'html.parser')
        text = soup.get_text()[:500]
        return strip_tags(text)

    def item_pubdate(self, item):
        return item.time_create

    def item_updateddate(self, item):
        return item.time_update

    def item_author_name(self, item):
        return item.author.username if item.author else "Unknown"

    def item_categories(self, item):
        categories = [item.cat.name] if item.cat else []
        tags = [tag.tag for tag in item.tags.all()]
        return categories + tags

    def item_link(self, item):
        return item.get_absolute_url()

    def item_enclosures(self, item):
        """Добавляем изображение статьи как enclosure"""
        if item.photo:
            return [feedgenerator.Enclosure(
                url=item.photo.url,
                length=str(0),  # Неизвестная длина
                mime_type="image/jpeg",
            )]
        return []


class CategoryPostsFeed(LatestPostsFeed):
    """RSS лента статей категории"""
    def get_object(self, request, cat_slug):
        from main.models import Category
        return Category.objects.get(slug=cat_slug)

    def title(self, obj):
        return f"PageGlow - Категория: {obj.name}"

    def description(self, obj):
        return f"Статьи из категории '{obj.name}'"

    def link(self, obj):
        return obj.get_absolute_url()

    def items(self, obj):
        return Post.published.filter(cat=obj).order_by('-time_create')[:30]


class TagPostsFeed(LatestPostsFeed):
    """RSS лента статей по тегу"""
    def get_object(self, request, tag_slug):
        from main.models import TagPost
        return TagPost.objects.get(slug=tag_slug)

    def title(self, obj):
        return f"PageGlow - Тег: {obj.tag}"

    def description(self, obj):
        return f"Статьи с тегом '{obj.tag}'"

    def link(self, obj):
        return obj.get_absolute_url()

    def items(self, obj):
        return Post.published.filter(tags=obj).order_by('-time_create')[:30]


class AtomLatestPostsFeed(LatestPostsFeed):
    """Atom лента последних статей"""
    feed_type = feedgenerator.Atom1Feed
    subtitle = LatestPostsFeed.description


# ===== FULL CONTENT FEEDS =====

class FullContentPostsFeed(Feed):
    """RSS лента с полным содержимым статей"""
    title = "PageGlow - Полные статьи"
    link = "/"
    description = "Полные версии последних статей"

    def items(self):
        return Post.published.select_related('author', 'cat').order_by('-time_create')[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        # Возвращаем полный HTML контент
        return item.content

    def item_pubdate(self, item):
        return item.time_create

    def item_author_name(self, item):
        return item.author.username if item.author else "Unknown"

    def item_link(self, item):
        return item.get_absolute_url()

    def item_enclosures(self, item):
        """Добавляем изображение как enclosure"""
        if item.photo:
            return [feedgenerator.Enclosure(
                url=item.photo.url,
                length=str(0),
                mime_type="image/jpeg",
            )]
        return []
