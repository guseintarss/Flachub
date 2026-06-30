from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PostViewSet, CategoryViewSet, TagViewSet,
    CommentViewSet, CommentLikeViewSet,
    NotificationViewSet, BookmarkViewSet, CollectionViewSet,
    UserStatsViewSet, PostLikeViewSet, MediaUploadViewSet,
    current_user, sidebar_data, login_view, logout_view,
    register_view, password_change_view,
    password_reset_view, password_reset_confirm_view,
    subscription_feed_view
)

router = DefaultRouter()

# Основные ресурсы
router.register(r'posts', PostViewSet, basename='post')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'tags', TagViewSet, basename='tag')

# Комментарии (nested под постами)
router.register(r'comments', CommentViewSet, basename='comment')

# Уведомления
router.register(r'notifications', NotificationViewSet, basename='notification')

# Закладки и коллекции
router.register(r'bookmarks', BookmarkViewSet, basename='bookmark')
router.register(r'collections', CollectionViewSet, basename='collection')

# Пользователи и статистика
router.register(r'users', UserStatsViewSet, basename='user-stats')

# Действия (лайки, избранное)
router.register(r'post-actions', PostLikeViewSet, basename='post-actions')
router.register(r'comment-actions', CommentLikeViewSet, basename='comment-actions')

# Медиа
router.register(r'media', MediaUploadViewSet, basename='media')

urlpatterns = [
    path('', include(router.urls)),
    path('sidebar/', sidebar_data, name='sidebar-data'),
    path('me/', current_user, name='current-user'),
    path('auth/login/', login_view, name='auth-login'),
    path('auth/logout/', logout_view, name='auth-logout'),
    path('auth/register/', register_view, name='auth-register'),
    path('password/change/', password_change_view, name='password-change'),
    path('auth/password-reset/', password_reset_view, name='password-reset'),
    path('auth/password-reset/confirm/', password_reset_confirm_view, name='password-reset-confirm'),
    path('subscriptions/feed/', subscription_feed_view, name='subscription-feed'),
]
