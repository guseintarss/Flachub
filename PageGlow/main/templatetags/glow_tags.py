"""Шаблонные теги для базового шаблона и страниц ошибок."""
from django import template
from django.db.models import Count, Q

from main.models import Category

register = template.Library()


@register.inclusion_tag('main/list_categories.html')
def show_categories(cat_selected=0):
    """Показать категории с опубликованными постами и их количеством."""
    cats = Category.objects.annotate(
        posts_count=Count('posts', filter=Q(posts__is_published=True)),
    ).filter(posts_count__gt=0).order_by('name')
    return {'cats': cats, 'cat_selected': cat_selected}
