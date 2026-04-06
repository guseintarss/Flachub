from django import template
import main.views as views
from main.forms import AddPostForm
from main.models import Category, TagPost
from main.utils import menu
from django.db.models import Count, Q

register = template.Library()

@register.simple_tag
def get_menu():
    return menu

@register.inclusion_tag('main/list_categories.html')
def show_categories(cat_selected=0):
    # Показываем только категории с опубликованными постами
    cats = Category.objects.annotate(
        posts_count=Count(
            'posts',
            filter=Q(posts__is_published=True)
        )
    ).filter(posts_count__gt=0).order_by('name')
    return {'cats': cats, 'cat_selected': cat_selected}

@register.inclusion_tag('main/list_tags.html')
def show_all_tags():
    return {'tags': TagPost.objects.all()}
