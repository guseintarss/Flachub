from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PostViewSet, CategoryViewSet, TagViewSet,
    CommentViewSet, CommentLikeViewSet,
    NotificationViewSet, BookmarkViewSet, CollectionViewSet,
    UserStatsViewSet, PostLikeViewSet, MediaUploadViewSet,
    sidebar_data
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
]
