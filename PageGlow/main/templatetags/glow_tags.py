from django import template
import main.views as views
from main.forms import AddPostForm
from main.models import Category, TagPost
from main.utils import menu

register = template.Library()

@register.simple_tag
def get_menu():
    return menu

@register.inclusion_tag('main/list_categories.html')
def show_categories(cat_selected=0):
    cats = Category.objects.all()
    return {'cats': cats, 'cat_selected': cat_selected}

@register.inclusion_tag('main/list_tags.html')
def show_all_tags():
    return {'tags': TagPost.objects.all()}
