from rest_framework import viewsets, status, permissions, mixins
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Count, Prefetch
from django.contrib.auth import get_user_model

from main.models import (
    Post, Category, TagPost, Comment, 
    Notification, Bookmark, Collection,
    UserAchievement
)
from .serializers import (
    PostListSerializer, PostDetailSerializer, PostCreateUpdateSerializer,
    CategorySerializer, TagSerializer,
    CommentSerializer, CommentCreateSerializer,
    NotificationSerializer,
    BookmarkSerializer, BookmarkCreateSerializer,
    CollectionSerializer,
    UserAchievementSerializer,
    UserPublicSerializer
)

User = get_user_model()


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# ===== Post ViewSet =====

class PostViewSet(viewsets.ModelViewSet):
    """
    API для постов: список, детали, создание, обновление, удаление
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['post_type', 'cat', 'is_published']
    search_fields = ['title', 'content']
    ordering_fields = ['time_create', 'time_update', 'views', 'title']
    ordering = ['-time_create']

    def get_queryset(self):
        queryset = Post.published.select_related('cat', 'author').prefetch_related('tags')
        
        # Фильтр по тегам
        tag_slug = self.request.query_params.get('tag', None)
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        
        # Фильтр по категории (slug)
        cat_slug = self.request.query_params.get('cat', None)
        if cat_slug:
            queryset = queryset.filter(cat__slug=cat_slug)
        
        # Фильтр по автору
        author_id = self.request.query_params.get('author', None)
        if author_id:
            queryset = queryset.filter(author_id=author_id)
        
        # Поиск
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )
        
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PostCreateUpdateSerializer
        return PostDetailSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def retrieve(self, request, *args, **kwargs):
        # Увеличиваем счетчик просмотров
        instance = self.get_object()
        instance.views += 1
        instance.save(update_fields=['views'])
        return super().retrieve(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


# ===== Category ViewSet =====

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API для категорий (только чтение)
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'


# ===== Tag ViewSet =====

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API для тегов (только чтение)
    """
    queryset = TagPost.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'


# ===== Comment ViewSet =====

class CommentViewSet(viewsets.ModelViewSet):
    """
    API для комментариев: создание, обновление, удаление
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        post_id = self.kwargs.get('post_pk')
        return Comment.objects.filter(
            post_id=post_id, 
            is_active=True
        ).select_related('author', 'post').prefetch_related('likes')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CommentCreateSerializer
        return CommentSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_pk')
        serializer.save(
            author=self.request.user,
            post_id=post_id
        )

    def perform_destroy(self, instance):
        # Мягкое удаление
        instance.is_active = False
        instance.save()


# ===== Comment Like Action =====

class CommentLikeViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    """
    API для лайков комментариев
    """
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def toggle_like(self, request, pk=None):
        comment = Comment.objects.get(pk=pk)
        user = request.user
        
        if comment.likes.filter(id=user.id).exists():
            comment.likes.remove(user)
            liked = False
        else:
            comment.likes.add(user)
            liked = True
        
        return Response({
            'liked': liked,
            'likes_count': comment.number_of_likes()
        })


# ===== Notification ViewSet =====

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API для уведомлений: список, детали, отметка прочитанными
    """
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related('sender', 'post')

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Отметить все уведомления как прочитанные"""
        self.get_queryset().update(is_read=True)
        return Response({'status': 'all marked as read'})

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Отметить конкретный уведомление как прочитанный"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'marked as read'})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Количество непрочитанных уведомлений"""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})


# ===== Bookmark ViewSet =====

class BookmarkViewSet(viewsets.ModelViewSet):
    """
    API для закладок: создание, получение, удаление
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Bookmark.objects.filter(
            user=self.request.user
        ).select_related('post', 'collection')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return BookmarkCreateSerializer
        return BookmarkSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ===== Collection ViewSet =====

class CollectionViewSet(viewsets.ModelViewSet):
    """
    API для коллекций: создание, получение, обновление, удаление
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CollectionSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Collection.objects.filter(
            user=self.request.user
        ).prefetch_related('bookmarks')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ===== User Stats ViewSet =====

class UserStatsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API для статистики пользователя
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserPublicSerializer

    def get_queryset(self):
        return User.objects.all()

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        user = self.get_object()
        
        posts_count = user.posts.filter(is_published=Post.Status.PUBLISHED).count()
        comments_count = user.comments.filter(is_active=True).count()
        likes_received = Post.objects.filter(author=user).aggregate(
            total_likes=Count('likes')
        )['total_likes'] or 0
        
        return Response({
            'posts_count': posts_count,
            'comments_count': comments_count,
            'likes_received': likes_received,
            'followers_count': user.subscribers.count(),
            'following_count': user.subscriptions.count(),
        })

    @action(detail=True, methods=['get'])
    def achievements(self, request, pk=None):
        user = self.get_object()
        achievements = UserAchievement.objects.filter(user=user).select_related('badge')
        serializer = UserAchievementSerializer(achievements, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        user = self.get_object()
        posts = Post.published.filter(author=user).select_related('cat', 'author')
        
        # Пагинация
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = PostListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = PostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def favorites(self, request, pk=None):
        user = self.get_object()
        if request.user.id != user.id:
            return Response({'error': 'Доступ запрещен'}, status=403)
        
        favorites = Post.objects.filter(favorites=user).select_related('cat', 'author')
        page = self.paginate_queryset(favorites)
        if page is not None:
            serializer = PostListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = PostListSerializer(favorites, many=True, context={'request': request})
        return Response(serializer.data)


# ===== Post Like Action ViewSet =====

class PostLikeViewSet(viewsets.GenericViewSet):
    """
    API для лайков постов
    """
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def toggle_like(self, request, pk=None):
        """Переключить лайк поста"""
        post = Post.objects.get(pk=pk)
        user = request.user
        
        if post.likes.filter(id=user.id).exists():
            post.likes.remove(user)
            liked = False
        else:
            post.likes.add(user)
            liked = True
        
        return Response({
            'liked': liked,
            'likes_count': post.number_of_likes()
        })

    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        """Переключить избранное поста"""
        post = Post.objects.get(pk=pk)
        user = request.user
        
        if post.favorites.filter(id=user.id).exists():
            post.favorites.remove(user)
            favorited = False
        else:
            post.favorites.add(user)
            favorited = True
        
        return Response({
            'favorited': favorited,
            'favorites_count': post.number_of_favorites()
        })


# ===== File Upload ViewSet =====

from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.conf import settings
import os

class MediaUploadViewSet(viewsets.GenericViewSet):
    """
    API для загрузки медиафайлов (изображения)
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @action(detail=False, methods=['post'])
    def upload_image(self, request):
        """Загрузка изображения"""
        image = request.FILES.get('image')
        if not image:
            return Response(
                {'error': 'Изображение не предоставлено'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Валидация типа файла
        if not image.content_type.startswith('image/'):
            return Response(
                {'error': 'Поддерживаются только изображения'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Валидация размера (5MB максимум)
        if image.size > 5 * 1024 * 1024:
            return Response(
                {'error': 'Размер файла не должен превышать 5MB'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Сохранение файла
        filename = default_storage.save(f'uploads/{image.name}', image)
        file_url = default_storage.url(filename)
        
        return Response({
            'url': file_url,
            'filename': filename
        })


# ===== Sidebar Data =====

@api_view(['GET'])
@permission_classes([AllowAny])
def current_user(request):
    """Возвращает данные текущего пользователя или null"""
    if request.user.is_authenticated:
        serializer = UserPublicSerializer(request.user, context={'request': request})
        data = serializer.data
        data['is_staff'] = request.user.is_staff
        data['is_superuser'] = request.user.is_superuser
        return Response(data)
    return Response(None)


@api_view(['GET'])
@permission_classes([AllowAny])
def sidebar_data(request):
    posts = Post.objects.filter(
        is_published=True
    ).select_related('author', 'cat').annotate(
        likes_count=Count('likes', distinct=True)
    ).order_by('-time_create')[:5]

    categories = Category.objects.annotate(
        posts_count=Count('posts', filter=Q(posts__is_published=True))
    ).filter(posts_count__gt=0).order_by('-posts_count')[:10]

    return Response({
        'recent_posts': [
            {
                'id': p.id,
                'title': p.title,
                'slug': p.slug,
                'photo': p.photo.url if p.photo else None,
                'author': p.author.username if p.author else 'Аноним',
                'time_create': p.time_create.isoformat(),
                'views': p.views,
                'likes_count': getattr(p, 'likes_count', 0),
            }
            for p in posts
        ],
        'categories': [
            {
                'id': c.id,
                'name': c.name,
                'slug': c.slug,
                'posts_count': getattr(c, 'posts_count', 0),
            }
            for c in categories
        ],
        'tags': [],
        'stats': {
            'total_posts': Post.objects.count(),
            'total_users': User.objects.filter(is_active=True).count(),
            'total_comments': Comment.objects.count(),
        },
    })
