from django.urls import path

from . import views
from .feeds import (
    LatestPostsFeed, CategoryPostsFeed, TagPostsFeed,
    FullContentPostsFeed, AtomLatestPostsFeed
)


urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('upload/', views.CKEditorUploadView.as_view(), name='ckeditor_upload'),
    path('ajax/subscribe/', views.toggle_subscribe, name='toggle_subscribe'),

    # RSS/Atom feeds
    path('rss/', LatestPostsFeed(), name='rss_feed'),
    path('rss/full/', FullContentPostsFeed(), name='rss_full_feed'),
    path('atom/', AtomLatestPostsFeed(), name='atom_feed'),
    path('category/<slug:cat_slug>/rss/', CategoryPostsFeed(), name='category_rss_feed'),
    path('tag/<slug:tag_slug>/rss/', TagPostsFeed(), name='tag_rss_feed'),
]
