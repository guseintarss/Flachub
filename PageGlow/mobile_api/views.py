from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import viewsets, status, permissions, mixins
from rest_framework.decorators import action, api_view, permission_classes, authentication_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Count, Prefetch
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from main.models import (
    Post, Category, TagPost, Comment, 
    Notification, Bookmark, Collection,
    UserAchievement, Subscription
)
from users.models import UserReputationLog
from .serializers import (
    PostListSerializer, PostDetailSerializer, PostCreateUpdateSerializer,
    CategorySerializer, TagSerializer,
    CommentWithRepliesSerializer, CommentSerializer, CommentCreateSerializer,
    NotificationSerializer,
    BookmarkSerializer, BookmarkCreateSerializer,
    CollectionSerializer,
    UserAchievementSerializer,
    UserPublicSerializer, UserProfileSerializer
)

User = get_user_model()


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# ===== Post ViewSet =====

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return

@method_decorator(csrf_exempt, name='dispatch')
class PostViewSet(viewsets.ModelViewSet):
    """
    API для постов: список, детали, создание, обновление, удаление
    """
    authentication_classes = [CsrfExemptSessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['post_type', 'is_published', 'author']
    search_fields = ['title', 'content', 'author__username', 'author__first_name', 'author__last_name']
    ordering_fields = ['time_create', 'time_update', 'views', 'title']
    ordering = ['-time_create']

    def get_queryset(self):
        is_published_param = self.request.query_params.get('is_published', None)
        author_id = self.request.query_params.get('author', None)

        # Если запрошены черновики (is_published=0), используем objects и проверяем права
        if is_published_param == '0' and author_id:
            if self.request.user.is_authenticated and str(self.request.user.id) == author_id:
                queryset = Post.objects.filter(is_published=Post.Status.DRAFT)
            else:
                return Post.objects.none()
        else:
            queryset = Post.published.all()

        # Для retrieve/update — автор может получить свои посты (включая черновики)
        if self.action in ('retrieve', 'update', 'partial_update') and self.request.user.is_authenticated:
            queryset = Post.objects.filter(
                Q(is_published=Post.Status.PUBLISHED) | Q(author=self.request.user)
            )

        # Для destroy — только автор может удалить свой пост
        if self.action == 'destroy' and self.request.user.is_authenticated:
            queryset = Post.objects.filter(author=self.request.user)

        queryset = queryset.select_related('cat', 'author').prefetch_related('tags')
        
        # Фильтр по тегам
        tag_slug = self.request.query_params.get('tag', None)
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        
        # Фильтр по категории (slug)
        cat_slug = self.request.query_params.get('cat', None)
        if cat_slug:
            queryset = queryset.filter(cat__slug=cat_slug)
        
        # Фильтр по автору
        if author_id:
            queryset = queryset.filter(author_id=author_id)
        
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
        post = serializer.save(author=self.request.user)
        UserReputationLog.objects.create(
            user=post.author,
            amount=10,
            reason='post_created',
            post=post
        )
        from django.core.cache import cache
        cache.delete(f'user_reputation_{post.author.id}')

    def perform_destroy(self, instance):
        author = instance.author
        if author:
            author.add_reputation(amount=-10, reason=UserReputationLog.ReasonType.POST_DELETED, post=instance)
        from django.core.cache import cache
        cache.clear()
        instance.delete()


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
    permission_classes = [AllowAny]
    serializer_class = UserPublicSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['username', 'first_name', 'last_name', 'about_me']
    ordering_fields = ['date_joined', 'username', 'posts_count']
    ordering = ['-date_joined']

    def get_queryset(self):
        return User.objects.filter(is_active=True).annotate(
            posts_count=Count('posts')
        )

    @action(detail=True, methods=['get'])
    def profile(self, request, pk=None):
        """Полный профиль пользователя"""
        user = self.get_object()
        serializer = UserProfileSerializer(user, context={'request': request})
        data = serializer.data

        # Дополнительные данные
        published_posts = Post.published.filter(author=user).select_related('cat', 'author')
        drafts = Post.objects.filter(
            author=user,
            is_published=Post.Status.DRAFT
        ).select_related('cat', 'author')
        favorites = Post.objects.filter(favorites=user).select_related('cat', 'author')
        achievements = UserAchievement.objects.filter(user=user).select_related('badge')

        is_subscribed = False
        is_own = request.user.is_authenticated and request.user.id == user.id
        if request.user.is_authenticated and not is_own:
            is_subscribed = Subscription.objects.filter(subscriber=request.user, author=user).exists()

        data['is_own_profile'] = is_own
        data['is_subscribed'] = is_subscribed
        data['published_count'] = published_posts.count()
        data['drafts_count'] = drafts.count() if is_own else 0
        data['favorites_count'] = favorites.count() if is_own else 0
        data['achievements'] = UserAchievementSerializer(achievements, many=True).data

        return Response(data)

    @action(detail=False, methods=['get'], url_path='by-username/(?P<username>[^/.]+)')
    def by_username(self, request, username=None):
        """Найти пользователя по username"""
        user = get_object_or_404(User, username=username, is_active=True)
        serializer = UserProfileSerializer(user, context={'request': request})
        data = serializer.data

        published_posts = Post.published.filter(author=user).select_related('cat', 'author')
        achievements = UserAchievement.objects.filter(user=user).select_related('badge')

        is_subscribed = False
        is_own = request.user.is_authenticated and request.user.id == user.id
        if request.user.is_authenticated and not is_own:
            is_subscribed = Subscription.objects.filter(subscriber=request.user, author=user).exists()

        data['is_own_profile'] = is_own
        data['is_subscribed'] = is_subscribed
        data['published_count'] = published_posts.count()
        data['achievements'] = UserAchievementSerializer(achievements, many=True).data

        return Response(data)

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
            'followers_count': Subscription.objects.filter(author=user).count(),
            'following_count': Subscription.objects.filter(subscriber=user).count(),
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


# ===== Auth =====

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    from django.contrib.auth import authenticate, login
    username = request.data.get('username', '')
    password = request.data.get('password', '')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        serializer = UserPublicSerializer(user, context={'request': request})
        return Response(serializer.data)
    return Response({'error': 'Неверный логин или пароль'}, status=400)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    return Response({'status': 'ok'})


# ===== Registration =====

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    from users.forms import RegisterUserForm
    form = RegisterUserForm(request.data)
    if form.is_valid():
        user = form.save()
        user.banner_gradient_start = '#0c6acf'
        user.banner_gradient_end = '#764ba2'
        user.save(update_fields=['banner_gradient_start', 'banner_gradient_end'])
        from django.contrib.auth import authenticate, login
        user = authenticate(request, username=user.username, password=form.cleaned_data.get('password1'))
        login(request, user)
        serializer = UserPublicSerializer(user, context={'request': request})
        return Response(serializer.data, status=201)
    return Response({'errors': form.errors}, status=400)


# ===== Sidebar Data =====

@csrf_exempt
@api_view(['GET', 'PATCH'])
@authentication_classes([CsrfExemptSessionAuthentication, JWTAuthentication])
@permission_classes([AllowAny])
def current_user(request):
    """Возвращает или обновляет данные текущего пользователя"""
    if not request.user.is_authenticated:
        return Response(None)

    if request.method == 'PATCH':
        user = request.user
        data = request.data

        # Только разрешённые поля
        allowed_fields = ['first_name', 'last_name', 'about_me',
                          'banner_gradient_start', 'banner_gradient_end',
                          'show_email', 'show_phone', 'show_birth_date']
        for field in allowed_fields:
            if field in data:
                value = data[field]
                if field in ('show_email', 'show_phone', 'show_birth_date'):
                    value = value in ('1', 'true', 'True', True, 1)
                setattr(user, field, value)

        # Обработка аватара
        if 'photo' in request.FILES:
            user.photo = request.FILES['photo']
        elif data.get('photo_clear') == 'true':
            if user.photo:
                user.photo.delete(save=False)
                user.photo = None

        # Обработка баннера
        if 'banner_image' in request.FILES:
            user.banner_image = request.FILES['banner_image']
        if data.get('banner_image_clear') == 'true':
            if user.banner_image:
                user.banner_image.delete(save=False)
                user.banner_image = None

        # Обработка телефона
        if 'phone_namber' in data:
            if data['phone_namber']:
                cleaned = ''.join(filter(lambda x: x.isdigit(), data['phone_namber']))
                if cleaned.startswith('8'):
                    cleaned = '7' + cleaned[1:]
                if not cleaned.startswith('7'):
                    cleaned = '7' + cleaned
                user.phone_namber = cleaned[:11]
            else:
                user.phone_namber = None

        # Обработка даты рождения
        if 'data_birth' in data:
            if data['data_birth']:
                from django.utils.dateparse import parse_date
                from datetime import datetime
                parsed = parse_date(data['data_birth'])
                if parsed:
                    user.data_birth = datetime.combine(parsed, datetime.min.time())
            else:
                user.data_birth = None

        user.save()
        user.refresh_from_db()
        serializer = UserProfileSerializer(user, context={'request': request})
        data = serializer.data
        achievements = UserAchievement.objects.filter(user=user).select_related('badge')
        data['achievements'] = UserAchievementSerializer(achievements, many=True).data
        return Response(data)

    user = request.user
    serializer = UserProfileSerializer(user, context={'request': request})
    data = serializer.data
    achievements = UserAchievement.objects.filter(user=user).select_related('badge')
    data['achievements'] = UserAchievementSerializer(achievements, many=True).data
    return Response(data)


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

    tags = TagPost.objects.annotate(
        posts_count=Count('tags', filter=Q(tags__is_published=True))
    ).filter(posts_count__gt=0).order_by('-posts_count')[:15]

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
        'tags': [
            {
                'id': t.id,
                'name': t.tag,
                'slug': t.slug,
                'posts_count': getattr(t, 'posts_count', 0),
            }
            for t in tags
        ],
        'stats': {
            'total_posts': Post.objects.count(),
            'total_users': User.objects.filter(is_active=True).count(),
            'total_comments': Comment.objects.count(),
        },
    })


@csrf_exempt
@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
def password_change_view(request):
    from django.contrib.auth.password_validation import validate_password
    from django.core.exceptions import ValidationError

    user = request.user
    old_password = request.data.get('old_password', '')
    new_password1 = request.data.get('new_password1', '')
    new_password2 = request.data.get('new_password2', '')

    if not user.check_password(old_password):
        return Response({'error': 'Старый пароль неверен'}, status=400)

    if not new_password1:
        return Response({'error': 'Введите новый пароль'}, status=400)

    if new_password1 != new_password2:
        return Response({'error': 'Новые пароли не совпадают'}, status=400)

    if old_password == new_password1:
        return Response({'error': 'Новый пароль должен отличаться от старого'}, status=400)

    try:
        validate_password(new_password1, user=user)
    except ValidationError as e:
        return Response({'error': ' '.join(e.messages)}, status=400)

    user.set_password(new_password1)
    user.save(update_fields=['password'])

    from django.contrib.auth import update_session_auth_hash
    update_session_auth_hash(request, user)

    return Response({'status': 'ok', 'detail': 'Пароль успешно изменён'})


# ===== Password Reset =====

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_view(request):
    from django.contrib.auth.forms import PasswordResetForm
    email = request.data.get('email', '')
    if not email:
        return Response({'error': 'Введите email'}, status=400)

    form = PasswordResetForm({'email': email})
    if not form.is_valid():
        return Response({'error': 'Пользователь с таким email не найден'}, status=400)

    form.save(
        request=request,
        use_https=request.is_secure(),
        email_template_name='mobile_api/password_reset_email.html',
        subject_template_name='mobile_api/password_reset_subject.txt',
    )
    return Response({'status': 'ok', 'detail': 'Письмо для сброса пароля отправлено на ваш email'})


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm_view(request):
    from django.contrib.auth.forms import SetPasswordForm
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import urlsafe_base64_decode
    from django.contrib.auth import get_user_model

    uidb64 = request.data.get('uidb64', '')
    token = request.data.get('token', '')
    new_password1 = request.data.get('new_password1', '')
    new_password2 = request.data.get('new_password2', '')

    if not uidb64 or not token:
        return Response({'error': 'Неверная ссылка сброса пароля'}, status=400)

    if not new_password1 or not new_password2:
        return Response({'error': 'Введите новый пароль'}, status=400)

    if new_password1 != new_password2:
        return Response({'error': 'Пароли не совпадают'}, status=400)

    User = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({'error': 'Неверная ссылка сброса пароля'}, status=400)

    if not default_token_generator.check_token(user, token):
        return Response({'error': 'Срок действия ссылки истёк или она неверна'}, status=400)

    from django.contrib.auth.password_validation import validate_password
    from django.core.exceptions import ValidationError
    try:
        validate_password(new_password1, user=user)
    except ValidationError as e:
        return Response({'error': ' '.join(e.messages)}, status=400)

    user.set_password(new_password1)
    user.save(update_fields=['password'])

    return Response({'status': 'ok', 'detail': 'Пароль успешно сброшен'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subscription_feed_view(request):
    user = request.user

    subscribed_authors = User.objects.filter(
        subscribers__subscriber=user
    ).annotate(
        posts_count=Count('posts', filter=Q(posts__is_published=True))
    ).prefetch_related(
        Prefetch('posts',
            queryset=Post.published.select_related('cat').prefetch_related('tags')[:5],
            to_attr='recent_posts'
        )
    )

    authors_data = []
    for author in subscribed_authors:
        authors_data.append({
            'id': author.id,
            'username': author.username,
            'first_name': author.first_name,
            'last_name': author.last_name,
            'avatar': author.photo.url if author.photo else None,
            'bio': author.about_me or '',
            'posts_count': author.posts_count,
            'last_post': PostListSerializer(
                author.recent_posts[0], context={'request': request}
            ).data if author.recent_posts else None,
        })

    subscribed_ids = list(subscribed_authors.values_list('id', flat=True))

    posts = Post.published.filter(
        author_id__in=subscribed_ids
    ).select_related(
        'author', 'cat'
    ).prefetch_related(
        'tags', 'likes', 'favorites'
    ).order_by('-time_create')

    paginator = StandardResultsSetPagination()
    page = paginator.paginate_queryset(posts, request)
    posts_serializer = PostListSerializer(page, many=True, context={'request': request})

    return Response({
        'authors': authors_data,
        'posts': posts_serializer.data,
        'count': paginator.page.paginator.count if paginator.page else 0,
        'total_pages': paginator.page.paginator.num_pages if paginator.page else 0,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_stats_view(request):
    if not request.user.is_staff:
        return Response({'error': 'Доступ запрещён'}, status=403)

    from main.models import Post, Comment

    return Response({
        'total_users': User.objects.count(),
        'total_posts': Post.objects.count(),
        'published_posts': Post.published.count(),
        'total_comments': Comment.objects.filter(is_active=True).count(),
        'total_admins': User.objects.filter(is_superuser=True).count(),
        'total_moderators': User.objects.filter(is_staff=True, is_superuser=False).count(),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_users_view(request):
    if not request.user.is_staff:
        return Response({'error': 'Доступ запрещён'}, status=403)

    search = request.query_params.get('search', '')
    role = request.query_params.get('role', '')
    page = request.query_params.get('page', 1)

    users = User.objects.all().select_related('current_level')

    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )

    if role == 'admin':
        users = users.filter(is_superuser=True)
    elif role == 'moderator':
        users = users.filter(is_staff=True, is_superuser=False)
    elif role == 'user':
        users = users.filter(is_staff=False, is_superuser=False)

    users = users.order_by('-date_joined')

    paginator = StandardResultsSetPagination()
    paginator.page_size = 30
    page_obj = paginator.paginate_queryset(users, request)

    from .serializers import UserPublicSerializer
    serializer = UserPublicSerializer(page_obj, many=True, context={'request': request})

    return Response({
        'users': serializer.data,
        'count': paginator.page.paginator.count if paginator.page else 0,
        'total_pages': paginator.page.paginator.num_pages if paginator.page else 0,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_update_role_view(request, user_id):
    if not request.user.is_superuser:
        return Response({'error': 'Только администратор может изменять роли'}, status=403)

    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'Пользователь не найден'}, status=404)

    if target_user == request.user:
        return Response({'error': 'Нельзя изменить свою роль'}, status=400)

    role = request.data.get('role', '')
    if role not in ('user', 'moderator', 'admin'):
        return Response({'error': 'Недопустимая роль. Допустимо: user, moderator, admin'}, status=400)

    target_user.is_superuser = (role == 'admin')
    target_user.is_staff = (role in ('admin', 'moderator'))
    target_user.save(update_fields=['is_superuser', 'is_staff'])

    return Response({
        'success': True,
        'user_id': target_user.id,
        'username': target_user.username,
        'role': role,
    })
