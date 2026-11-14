from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, status, permissions, mixins
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Count, Prefetch, F
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from main.models import (
    Post, Category, TagPost, Comment, 
    Notification, Bookmark, Collection,
    UserAchievement, Subscription,
    Chat, Message, ReviewRequest, ReviewOffer
)
from users.models import UserReputationLog
from main.analytics import build_author_dashboard, record_post_read
from main.habr_import import HabrImportError, import_habr_article
from main.github_import import GitHubImportError, import_github_source
from .serializers import (
    PostListSerializer, PostDetailSerializer, PostCreateUpdateSerializer,
    CategorySerializer, TagSerializer,
    CommentWithRepliesSerializer, CommentSerializer, CommentCreateSerializer,
    NotificationSerializer,
    BookmarkSerializer, BookmarkCreateSerializer,
    CollectionSerializer,
    UserAchievementSerializer,
    UserPublicSerializer, UserProfileSerializer,
    ReviewOfferSerializer, ReviewRequestSerializer,
    ChatListSerializer, ChatDetailSerializer, ChatCreateSerializer,
    MessageSerializer, MessageCreateSerializer,
)

User = get_user_model()


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# ===== Post ViewSet =====

class IsAuthorOrReadOnly(permissions.BasePermission):
    """Читать может любой, изменять — только автор или модератор."""

    message = 'Изменять этот объект может только его автор.'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author_id == request.user.id or request.user.is_staff


class PostViewSet(viewsets.ModelViewSet):
    """
    API для постов: список, детали, создание, обновление, удаление
    """
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    pagination_class = StandardResultsSetPagination
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['post_type', 'is_published', 'author', 'review_status']
    search_fields = ['title', 'content', 'author__username', 'author__first_name', 'author__last_name']
    ordering_fields = ['time_create', 'time_update', 'views', 'title']
    ordering = ['-time_create']

    def get_permissions(self):
        # claim/release проверяют права внутри действия по правилам разбора.
        if self.action in ('claim_review', 'release_review'):
            return [IsAuthenticated()]
        return super().get_permissions()

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

        queryset = queryset.select_related('cat', 'author', 'reviewer').prefetch_related('tags')
        
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
        instance = self.get_object()
        # Автор и черновики не должны накручивать просмотры.
        if instance.is_published and instance.author_id != request.user.id:
            Post.objects.filter(pk=instance.pk).update(views=F('views') + 1)
            instance.refresh_from_db(fields=['views'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def read(self, request, slug=None):
        """Зафиксировать чтение: глубину, время и источник.

        Не увеличивает Post.views — это делает retrieve. Здесь только
        аналитика для дашборда автора.
        """
        post = self.get_object()
        view = record_post_read(post, request, request.data or {})
        return Response({
            'ok': True,
            'scroll_depth': view.scroll_depth,
            'is_read_complete': view.is_read_complete,
        })

    def _award_post_created(self, post):
        """Начислить репутацию за первую публикацию, без повторов при переопубликации."""
        if not post.is_published or not post.author:
            return
        already_awarded = UserReputationLog.objects.filter(
            user=post.author,
            reason=UserReputationLog.ReasonType.POST_CREATED,
            post=post,
        ).exists()
        if already_awarded:
            return
        post.author.add_reputation(
            amount=10,
            reason=UserReputationLog.ReasonType.POST_CREATED,
            post=post,
        )

    def perform_create(self, serializer):
        post = serializer.save(author=self.request.user)
        self._award_post_created(post)

    def perform_update(self, serializer):
        post = serializer.save()
        self._award_post_created(post)

    def perform_destroy(self, instance):
        author = instance.author
        if author and UserReputationLog.objects.filter(
            user=author,
            reason=UserReputationLog.ReasonType.POST_CREATED,
            post=instance,
        ).exists():
            author.add_reputation(
                amount=-10,
                reason=UserReputationLog.ReasonType.POST_DELETED,
                post=instance,
            )
        from django.core.cache import cache
        cache.clear()
        instance.delete()

    # ===== Review actions =====

    def _get_review_for_update(self, slug):
        return get_object_or_404(
            Post.objects.select_for_update(),
            slug=slug,
            post_type=Post.PostType.REVIEW,
            is_published=Post.Status.PUBLISHED,
        )

    @action(detail=True, methods=['post'])
    def claim_review(self, request, slug=None):
        """Взять разбор из очереди. Атомарно закрепляет ревьюера."""
        with transaction.atomic():
            post = self._get_review_for_update(slug)

            if post.author_id == request.user.id:
                raise PermissionDenied('Автор не может взять свой разбор')
            if post.review_status != Post.ReviewStatus.OPEN:
                raise ValidationError({'detail': 'Разбор уже взят или завершён'})

            post.reviewer = request.user
            post.review_status = Post.ReviewStatus.IN_REVIEW
            post.save(update_fields=['reviewer', 'review_status'])

            review_request, _ = ReviewRequest.objects.get_or_create(post=post)
            review_request.status = ReviewRequest.Status.IN_REVIEW
            review_request.selected_offer = None
            review_request.save(update_fields=['status', 'selected_offer', 'updated_at'])
            review_request.offers.filter(status=ReviewOffer.Status.PENDING).update(
                status=ReviewOffer.Status.DECLINED
            )

            if post.author_id:
                Notification.objects.create(
                    recipient=post.author,
                    sender=request.user,
                    notification_type=Notification.NotificationType.REVIEW_CLAIMED,
                    post=post,
                    message=f'{request.user.username} взял ваш разбор «{post.title[:100]}»',
                )

        return Response(self.get_serializer(post).data)

    @action(detail=True, methods=['post'])
    def release_review(self, request, slug=None):
        """Освободить разбор: доступно назначенному ревьюеру или staff."""
        with transaction.atomic():
            post = self._get_review_for_update(slug)

            if post.reviewer_id != request.user.id and not request.user.is_staff:
                raise PermissionDenied('Освободить разбор может ревьюер или модератор')
            if post.review_status != Post.ReviewStatus.IN_REVIEW:
                raise ValidationError({'detail': 'Разбор не в работе'})

            post.reviewer = None
            post.review_status = Post.ReviewStatus.OPEN
            post.save(update_fields=['reviewer', 'review_status'])

            review_request, _ = ReviewRequest.objects.get_or_create(post=post)
            review_request.status = ReviewRequest.Status.OPEN
            review_request.selected_offer = None
            review_request.save(update_fields=['status', 'selected_offer', 'updated_at'])
            review_request.offers.filter(status=ReviewOffer.Status.SELECTED).update(
                status=ReviewOffer.Status.WITHDRAWN
            )

        return Response(self.get_serializer(post).data)


# ===== Review Marketplace =====

class ReviewRequestViewSet(viewsets.ReadOnlyModelViewSet):
    """Маркетплейс разборов: открытые запросы и отклики ревьюеров."""

    serializer_class = ReviewRequestSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.action in ('offer', 'select_offer', 'withdraw_offer', 'cancel'):
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_queryset(self):
        queryset = ReviewRequest.objects.select_related(
            'post', 'post__author', 'post__cat', 'selected_offer',
        ).prefetch_related('offers__reviewer')

        user = self.request.user
        if user.is_authenticated:
            queryset = queryset.filter(
                Q(post__is_published=Post.Status.PUBLISHED) | Q(post__author=user)
            )
        else:
            queryset = queryset.filter(post__is_published=Post.Status.PUBLISHED)

        status_param = self.request.query_params.get('status', ReviewRequest.Status.OPEN)
        if status_param != 'all':
            if status_param not in ReviewRequest.Status.values:
                raise ValidationError({'status': 'Неизвестный статус запроса'})
            queryset = queryset.filter(status=status_param)

        if self.request.query_params.get('mine') == '1':
            if not user.is_authenticated:
                return queryset.none()
            queryset = queryset.filter(post__author=user)

        if self.request.query_params.get('reviewer') == 'me':
            if not user.is_authenticated:
                return queryset.none()
            queryset = queryset.filter(offers__reviewer=user).distinct()

        return queryset.order_by(F('deadline').asc(nulls_last=True), '-created_at')

    def _locked_request(self, pk):
        visibility = Q(post__is_published=Post.Status.PUBLISHED)
        user = self.request.user
        if user.is_authenticated:
            visibility |= Q(post__author=user)
            if user.is_staff:
                visibility = Q()
        return get_object_or_404(
            ReviewRequest.objects.select_for_update().select_related('post'),
            visibility,
            pk=pk,
        )

    def _author_only(self, review_request):
        if review_request.post.author_id != self.request.user.id and not self.request.user.is_staff:
            raise PermissionDenied('Управлять запросом может только автор разбора')

    @action(detail=True, methods=['post'])
    def offer(self, request, pk=None):
        """Оставить отклик. Повторный отклик обновляет предыдущий."""
        message = str((request.data or {}).get('message') or '').strip()
        price = (request.data or {}).get('price')
        deadline_days = (request.data or {}).get('deadline_days')

        if len(message) > 1000:
            raise ValidationError({'message': 'Сообщение не должно превышать 1000 символов'})
        if price in ('', None):
            price = None
        else:
            try:
                price = int(price)
            except (TypeError, ValueError):
                raise ValidationError({'price': 'Ставка должна быть числом'})
            if price < 0 or price > 10_000_000:
                raise ValidationError({'price': 'Ставка должна быть от 0 до 10 000 000 ₽'})
        if deadline_days in ('', None):
            deadline_days = None
        else:
            try:
                deadline_days = int(deadline_days)
            except (TypeError, ValueError):
                raise ValidationError({'deadline_days': 'Срок должен быть числом дней'})
            if deadline_days < 1 or deadline_days > 365:
                raise ValidationError({'deadline_days': 'Срок должен быть от 1 до 365 дней'})

        with transaction.atomic():
            review_request = self._locked_request(pk)
            if review_request.post.author_id == request.user.id:
                raise PermissionDenied('Автор не может откликнуться на свой разбор')
            if (
                review_request.status != ReviewRequest.Status.OPEN
                or review_request.post.review_status != Post.ReviewStatus.OPEN
            ):
                raise ValidationError({'detail': 'Запрос уже закрыт или взят в работу'})
            if review_request.deadline and review_request.deadline <= timezone.now():
                raise ValidationError({'detail': 'Срок приёма откликов истёк'})

            offer, created = ReviewOffer.objects.update_or_create(
                request=review_request,
                reviewer=request.user,
                defaults={
                    'message': message,
                    'price': price,
                    'deadline_days': deadline_days,
                    'status': ReviewOffer.Status.PENDING,
                },
            )
            if created and review_request.post.author_id:
                Notification.objects.create(
                    recipient=review_request.post.author,
                    sender=request.user,
                    notification_type=Notification.NotificationType.REVIEW_OFFER,
                    post=review_request.post,
                    message=f'{request.user.username} откликнулся на разбор «{review_request.post.title[:90]}»',
                )

        return Response(ReviewRequestSerializer(review_request, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def select_offer(self, request, pk=None):
        """Автор выбирает отклик: ревьюер закрепляется за разбором."""
        offer_id = (request.data or {}).get('offer_id')
        if not offer_id:
            raise ValidationError({'offer_id': 'Укажите отклик'})

        with transaction.atomic():
            review_request = self._locked_request(pk)
            self._author_only(review_request)
            if review_request.status != ReviewRequest.Status.OPEN:
                raise ValidationError({'detail': 'Запрос уже закрыт или взят в работу'})

            offer = get_object_or_404(
                ReviewOffer.objects.select_for_update().select_related('reviewer'),
                pk=offer_id,
                request=review_request,
            )
            if offer.status != ReviewOffer.Status.PENDING:
                raise ValidationError({'detail': 'Этот отклик больше недоступен'})

            review_request.offers.filter(status=ReviewOffer.Status.PENDING).exclude(
                pk=offer.pk
            ).update(status=ReviewOffer.Status.DECLINED)
            offer.status = ReviewOffer.Status.SELECTED
            offer.save(update_fields=['status', 'updated_at'])

            review_request.selected_offer = offer
            review_request.status = ReviewRequest.Status.IN_REVIEW
            review_request.save(update_fields=['selected_offer', 'status', 'updated_at'])

            post = review_request.post
            post.reviewer = offer.reviewer
            post.review_status = Post.ReviewStatus.IN_REVIEW
            post.save(update_fields=['reviewer', 'review_status'])

            Notification.objects.create(
                recipient=offer.reviewer,
                sender=request.user,
                notification_type=Notification.NotificationType.REVIEW_OFFER,
                post=post,
                message=f'Ваш отклик выбран: «{post.title[:100]}»',
            )

        return Response(ReviewRequestSerializer(review_request, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def withdraw_offer(self, request, pk=None):
        """Ревьюер отзывает свой отклик, пока его не выбрали."""
        with transaction.atomic():
            review_request = self._locked_request(pk)
            offer = get_object_or_404(
                ReviewOffer.objects.select_for_update(),
                request=review_request,
                reviewer=request.user,
            )
            if offer.status != ReviewOffer.Status.PENDING:
                raise ValidationError({'detail': 'Отозвать можно только отклик, ожидающий выбора'})
            offer.status = ReviewOffer.Status.WITHDRAWN
            offer.save(update_fields=['status', 'updated_at'])

        return Response(ReviewRequestSerializer(review_request, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Автор закрывает запрос, не выбирая ревьюера."""
        with transaction.atomic():
            review_request = self._locked_request(pk)
            self._author_only(review_request)
            if review_request.status not in (
                ReviewRequest.Status.OPEN,
                ReviewRequest.Status.IN_REVIEW,
            ):
                raise ValidationError({'detail': 'Этот запрос уже завершён'})

            review_request.offers.exclude(
                status=ReviewOffer.Status.WITHDRAWN
            ).update(status=ReviewOffer.Status.DECLINED)
            review_request.selected_offer = None
            review_request.status = ReviewRequest.Status.CANCELLED
            review_request.save(update_fields=['selected_offer', 'status', 'updated_at'])

            post = review_request.post
            post.reviewer = None
            post.review_status = Post.ReviewStatus.CANCELLED
            post.save(update_fields=['reviewer', 'review_status'])

        return Response(ReviewRequestSerializer(review_request, context={'request': request}).data)


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
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = Comment.objects.filter(is_active=True)
        # Комментарии к черновикам видны только автору черновика.
        if self.request.user.is_authenticated:
            qs = qs.filter(
                Q(post__is_published=Post.Status.PUBLISHED) | Q(post__author=self.request.user)
            )
        else:
            qs = qs.filter(post__is_published=Post.Status.PUBLISHED)
        qs = qs.select_related('author', 'post').prefetch_related('likes')
        post_id = self.kwargs.get('post_pk')
        if post_id:
            qs = qs.filter(post_id=post_id)
        return qs

    def get_permissions(self):
        # accept/resolve проверяют права внутри действия по правилам разбора.
        if self.action in ('accept', 'resolve'):
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CommentCreateSerializer
        return CommentSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def _get_comment_post(self, request):
        post_id = request.data.get('post_id')
        if not post_id:
            raise ValidationError({'post_id': 'Не указан пост'})
        try:
            post_id = int(post_id)
        except (TypeError, ValueError):
            raise ValidationError({'post_id': 'Некорректный идентификатор поста'})
        post = get_object_or_404(Post, pk=post_id)
        if not post.is_published and post.author_id != request.user.id:
            raise PermissionDenied('Нельзя комментировать чужой черновик')
        return post

    def create(self, request, *args, **kwargs):
        post = self._get_comment_post(request)
        context = self.get_serializer_context()
        context['post'] = post
        serializer = self.get_serializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)

        parent = serializer.validated_data.get('parent')
        if parent and parent.post_id != post.id:
            raise ValidationError({'parent': 'Родительский комментарий относится к другому посту'})

        comment = serializer.save(author=request.user, post=post)
        output = CommentSerializer(comment, context=self.get_serializer_context())
        self._broadcast_comment(post, output.data)
        self._notify_parent_author(post, comment, parent, request.user)
        headers = self.get_success_headers(output.data)
        return Response(output.data, status=status.HTTP_201_CREATED, headers=headers)

    @staticmethod
    def _broadcast_comment(post, payload):
        """Отправить комментарий подписчикам WebSocket-канала статьи."""
        try:
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer

            layer = get_channel_layer()
            if layer:
                async_to_sync(layer.group_send)(
                    f'comments_{post.id}',
                    {'type': 'comment_created', 'comment': payload},
                )
        except Exception:
            # Realtime — улучшение, а не условие сохранения комментария.
            import logging
            logging.getLogger(__name__).exception('comment broadcast failed')

    @staticmethod
    def _notify_parent_author(post, comment, parent, sender):
        if not parent or parent.author_id == sender.id:
            return
        notification = Notification.objects.create(
            recipient=parent.author,
            sender=sender,
            notification_type=Notification.NotificationType.COMMENT,
            post=post,
            comment=comment,
            message=f'{sender.username} ответил на ваш комментарий: «{post.title[:80]}»',
        )
        try:
            from main.consumers import send_notification_to_user
            from .serializers import NotificationSerializer
            send_notification_to_user(
                parent.author_id,
                NotificationSerializer(notification).data,
            )
        except Exception:
            import logging
            logging.getLogger(__name__).exception('comment notification push failed')

    def perform_update(self, serializer):
        comment = serializer.save()
        comment.is_edited = True
        comment.save(update_fields=['is_edited', 'updated_at'])

    def perform_destroy(self, instance):
        if instance.author != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("У вас нет прав для удаления этого комментария")
        instance.is_active = False
        instance.save(update_fields=['is_active'])

    # ===== Review actions =====

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Принять лучший разбор. Доступно только автору review-поста."""
        with transaction.atomic():
            comment = get_object_or_404(
                Comment.objects.select_for_update().select_related('post', 'author'),
                pk=pk,
                is_active=True,
            )
            post = comment.post

            if post.post_type != Post.PostType.REVIEW:
                raise ValidationError({'detail': 'Принять можно только комментарий к разбору'})
            if post.author_id != request.user.id:
                raise PermissionDenied('Принять разбор может только автор публикации')
            if comment.author_id == request.user.id:
                raise ValidationError({'detail': 'Нельзя принять собственный комментарий'})
            if comment.is_accepted:
                raise ValidationError({'detail': 'Комментарий уже принят'})
            if post.review_status == Post.ReviewStatus.COMPLETED:
                raise ValidationError({'detail': 'Разбор уже завершён'})

            comment.is_accepted = True
            comment.save(update_fields=['is_accepted'])

            post.review_status = Post.ReviewStatus.COMPLETED
            post.review_accepted_at = timezone.now()
            if post.reviewer_id is None:
                post.reviewer = comment.author
            post.save(update_fields=['review_status', 'review_accepted_at', 'reviewer'])

            already_awarded = UserReputationLog.objects.filter(
                user=comment.author,
                reason=UserReputationLog.ReasonType.ANSWER_ACCEPTED,
                comment=comment,
            ).exists()
            if not already_awarded:
                comment.author.add_reputation(
                    amount=15,
                    reason=UserReputationLog.ReasonType.ANSWER_ACCEPTED,
                    post=post,
                    comment=comment,
                )

            Notification.objects.create(
                recipient=comment.author,
                sender=request.user,
                notification_type=Notification.NotificationType.REVIEW_ACCEPTED,
                post=post,
                comment=comment,
                message=f'Ваш разбор принят: «{post.title[:100]}»',
            )

        return Response(CommentSerializer(comment, context=self.get_serializer_context()).data)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Переключить «решено» у строчного замечания."""
        comment = self.get_object()

        if comment.line_start is None:
            raise ValidationError({'detail': 'Решить можно только строчное замечание'})

        can_resolve = (
            comment.author_id == request.user.id
            or comment.post.author_id == request.user.id
            or request.user.is_staff
        )
        if not can_resolve:
            raise PermissionDenied('Решить замечание может автор комментария, автор разбора или модератор')

        comment.is_resolved = not comment.is_resolved
        comment.save(update_fields=['is_resolved'])
        return Response(CommentSerializer(comment, context=self.get_serializer_context()).data)


# ===== Comment Like Action =====

class CommentLikeViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    """
    API для лайков комментариев
    """
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def toggle_like(self, request, pk=None):
        comment = get_object_or_404(
            Comment,
            pk=pk,
            is_active=True,
            post__is_published=Post.Status.PUBLISHED,
        )
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
    pagination_class = StandardResultsSetPagination
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

        review_posts = Post.objects.filter(post_type=Post.PostType.REVIEW)
        completed_reviews = review_posts.filter(
            review_status=Post.ReviewStatus.COMPLETED
        )

        review_languages = list(
            completed_reviews.filter(reviewer=user)
            .exclude(code_language='')
            .values_list('code_language', flat=True)
            .distinct()
            .order_by('code_language')
        )

        line_comments = Comment.objects.filter(
            author=user,
            is_active=True,
            line_start__isnull=False,
            post__post_type=Post.PostType.REVIEW,
            post__is_published=Post.Status.PUBLISHED,
        )
        line_comments_total = line_comments.count()
        line_comments_accepted = line_comments.filter(is_accepted=True).count()

        return Response({
            'posts_count': posts_count,
            'comments_count': comments_count,
            'likes_received': likes_received,
            'followers_count': Subscription.objects.filter(author=user).count(),
            'following_count': Subscription.objects.filter(subscriber=user).count(),
            'reviews_given': completed_reviews.filter(reviewer=user).count(),
            'reviews_received': completed_reviews.filter(author=user).count(),
            'reviews_requested': review_posts.filter(
                author=user,
                is_published=Post.Status.PUBLISHED,
            ).count(),
            'review_languages': review_languages,
            'review_comments_count': line_comments_total,
            'review_comments_accepted': line_comments_accepted,
            'review_acceptance_rate': (
                round(line_comments_accepted / line_comments_total * 100)
                if line_comments_total else 0
            ),
            'review_offers_count': ReviewOffer.objects.filter(reviewer=user).count(),
        })

    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Разборы пользователя: given (default), received или requested."""
        user = self.get_object()
        role = request.query_params.get('role', 'given')

        queryset = Post.objects.filter(
            post_type=Post.PostType.REVIEW
        ).select_related('cat', 'author', 'reviewer')

        if role == 'given':
            queryset = queryset.filter(
                reviewer=user,
                review_status=Post.ReviewStatus.COMPLETED,
            )
        elif role == 'received':
            queryset = queryset.filter(
                author=user,
                review_status=Post.ReviewStatus.COMPLETED,
            )
        elif role == 'requested':
            # Посты других пользователей не должны раскрывать чужие черновики.
            queryset = queryset.filter(
                author=user,
                is_published=Post.Status.PUBLISHED,
            )
        else:
            raise ValidationError({'role': 'Допустимо: given, received, requested'})

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PostListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = PostListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

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
        post = get_object_or_404(Post.published, pk=pk)
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
        post = get_object_or_404(Post.published, pk=pk)
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
        
        # Валидация типа файла (SVG не принимаем: в нём может быть скрипт)
        allowed_types = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}
        if image.content_type not in allowed_types:
            return Response(
                {'error': 'Поддерживаются только JPEG, PNG, GIF и WebP'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Валидация размера (5MB максимум)
        if image.size > 5 * 1024 * 1024:
            return Response(
                {'error': 'Размер файла не должен превышать 5MB'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Имя и расширение генерируем сами: имя от пользователя может содержать
        # опасное расширение или путь.
        import uuid
        ext = {'image/jpeg': 'jpg', 'image/png': 'png', 'image/gif': 'gif', 'image/webp': 'webp'}[image.content_type]
        filename = default_storage.save(f'uploads/{uuid.uuid4().hex}.{ext}', image)
        file_url = default_storage.url(filename)
        
        return Response({
            'url': file_url,
            'filename': filename
        })


# ===== Chat / Direct Messages =====

class ChatViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin):
    """
    API для чатов: список, создание, детали, отправка сообщений
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Chat.objects.filter(
            participants=self.request.user
        ).prefetch_related('participants').annotate(
            unread_count=Count('messages', filter=~Q(messages__sender=self.request.user) & Q(messages__is_read=False))
        ).order_by('-updated_at')

    def get_serializer_class(self):
        if self.action == 'create':
            return ChatCreateSerializer
        elif self.action == 'retrieve':
            return ChatDetailSerializer
        return ChatListSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        participant_id = serializer.validated_data['participant_id']

        if participant_id == request.user.id:
            return Response({'error': 'Нельзя создать чат с самим собой'}, status=400)

        existing = Chat.objects.filter(participants=request.user).filter(participants=participant_id)
        if existing.exists():
            chat = existing.first()
            output = ChatDetailSerializer(chat, context=self.get_serializer_context())
            return Response(output.data, status=200)

        chat = Chat.objects.create()
        chat.participants.add(request.user.id, participant_id)
        output = ChatDetailSerializer(chat, context=self.get_serializer_context())
        return Response(output.data, status=201)

    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        chat = self.get_object()
        if request.user not in chat.participants.all():
            return Response({'error': 'Вы не участник этого чата'}, status=403)

        from django.utils import timezone
        from datetime import timedelta
        recent = chat.messages.filter(
            sender=request.user,
            text=request.data.get('text', '').strip(),
            created_at__gte=timezone.now() - timedelta(seconds=5)
        ).first()
        if recent:
            output = MessageSerializer(recent, context={'request': request})
            return Response(output.data, status=200)

        serializer = MessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save(chat=chat, sender=request.user)

        chat.last_message = message.text
        chat.last_message_time = message.created_at
        chat.last_message_sender = request.user
        chat.save(update_fields=['last_message', 'last_message_time', 'last_message_sender', 'updated_at'])

        output = MessageSerializer(message, context={'request': request})

        try:
            from main.consumers import send_chat_notification_to_user
            other_ids = list(chat.participants.exclude(id=request.user.id).values_list('id', flat=True))
            for other_id in other_ids:
                send_chat_notification_to_user(other_id, chat.id, request.user.username, message.text[:100])

            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f'chat_{chat.id}',
                    {
                        'type': 'chat_message',
                        'message': output.data,
                    }
                )
        except Exception as e:
            import logging
            logging.getLogger(__name__).exception(f'send_chat_notification failed: {e}')

        return Response(output.data, status=201)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        chat = self.get_object()
        if request.user not in chat.participants.all():
            return Response({'error': 'Доступ запрещён'}, status=403)

        # Mark incoming messages as read
        chat.messages.exclude(sender=request.user).filter(is_read=False).update(is_read=True)

        messages_qs = chat.messages.select_related('sender').order_by('created_at')
        page = self.paginate_queryset(messages_qs)
        if page is not None:
            serializer = MessageSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = MessageSerializer(messages_qs, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        chat = self.get_object()
        if request.user not in chat.participants.all():
            return Response({'error': 'Доступ запрещён'}, status=403)

        updated = chat.messages.exclude(sender=request.user).filter(is_read=False).update(is_read=True)
        return Response({'marked_read': updated})


# ===== Auth =====

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_protect
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


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_protect
def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    return Response({'status': 'ok'})


# ===== Registration =====

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_protect
def register_view(request):
    from users.forms import RegisterUserForm
    form = RegisterUserForm(request.data)
    if form.is_valid():
        user = form.save()
        user.banner_gradient_start = '#0c1f18'
        user.banner_gradient_end = '#2f7d5a'
        user.save(update_fields=['banner_gradient_start', 'banner_gradient_end'])
        from django.contrib.auth import authenticate, login
        user = authenticate(request, username=user.username, password=form.cleaned_data.get('password1'))
        login(request, user)
        serializer = UserPublicSerializer(user, context={'request': request})
        return Response(serializer.data, status=201)
    return Response({'errors': form.errors}, status=400)


# ===== Sidebar Data =====

@ensure_csrf_cookie
@api_view(['GET', 'PATCH'])
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


@api_view(['POST'])
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

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_protect
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


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_protect
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
def author_dashboard_view(request):
    """Дашборд автора: дочитывания, источники, подписчики."""
    try:
        days = int(request.query_params.get('days', 30))
    except (TypeError, ValueError):
        days = 30
    return Response(build_author_dashboard(request.user, days=days))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_habr_view(request):
    """Импортировать статью с Хабра в черновик редактора."""
    url = (request.data or {}).get('url', '')
    try:
        draft = import_habr_article(url)
    except HabrImportError as exc:
        return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        import logging
        logging.getLogger(__name__).exception('habr import failed')
        return Response(
            {'detail': 'Не удалось импортировать статью. Попробуйте другую ссылку.'},
            status=status.HTTP_502_BAD_GATEWAY,
        )
    return Response(draft)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_github_view(request):
    """Импортировать код из публичного репозитория, файла или PR."""
    url = (request.data or {}).get('url', '')
    try:
        draft = import_github_source(url)
    except GitHubImportError as exc:
        return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        import logging
        logging.getLogger(__name__).exception('github import failed')
        return Response(
            {'detail': 'Не удалось импортировать код из GitHub. Попробуйте другую ссылку.'},
            status=status.HTTP_502_BAD_GATEWAY,
        )
    return Response(draft)


@api_view(['GET'])
@permission_classes([AllowAny])
def review_spotlight_view(request):
    """«Разбор дня» и «Запрос недели» для главной."""
    completed = Post.published.filter(
        post_type=Post.PostType.REVIEW,
        review_status=Post.ReviewStatus.COMPLETED,
    ).select_related('author', 'cat', 'reviewer').prefetch_related('tags')

    completed_count = completed.count()
    review_of_day = None
    if completed_count:
        day_index = timezone.localdate().toordinal() % completed_count
        post = completed.order_by('-review_accepted_at', '-time_create')[day_index]
        review_of_day = PostListSerializer(post, context={'request': request}).data

    requests = Post.published.filter(
        post_type=Post.PostType.REVIEW,
        review_status=Post.ReviewStatus.OPEN,
        review_request__status=ReviewRequest.Status.OPEN,
    ).select_related('author', 'cat', 'review_request').annotate(
        pending_offers=Count(
            'review_request__offers',
            filter=Q(review_request__offers__status=ReviewOffer.Status.PENDING),
            distinct=True,
        )
    ).order_by('-pending_offers', '-views', '-time_create')

    request_of_week = None
    if review_of_day:
        requests = requests.exclude(pk=review_of_day['id'])
    post = requests.first()
    if not post and not review_of_day:
        post = Post.published.filter(
            post_type=Post.PostType.REVIEW,
            review_status=Post.ReviewStatus.OPEN,
        ).select_related('author', 'cat').first()
    if post:
        request_of_week = PostListSerializer(post, context={'request': request}).data

    return Response({
        'review_of_day': review_of_day,
        'request_of_week': request_of_week,
    })


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
    from django.db.models.functions import TruncDate
    from django.utils import timezone
    from datetime import timedelta

    days = 14
    since = timezone.now() - timedelta(days=days)

    daily_registrations = (
        User.objects
        .filter(date_joined__gte=since)
        .annotate(date=TruncDate('date_joined'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    daily_posts = (
        Post.objects
        .filter(time_create__gte=since)
        .annotate(date=TruncDate('time_create'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    daily_comments = (
        Comment.objects
        .filter(created_at__gte=since, is_active=True)
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    def fill_dates(qs):
        data = {}
        for r in qs:
            d = r['date']
            key = d.isoformat() if hasattr(d, 'isoformat') else str(d)
            data[key] = r['count']
        result = []
        for i in range(days - 1, -1, -1):
            d = (timezone.now() - timedelta(days=i)).date()
            result.append({'date': d.isoformat(), 'count': data.get(d.isoformat(), 0)})
        return result

    return Response({
        'total_users': User.objects.count(),
        'total_posts': Post.objects.count(),
        'published_posts': Post.published.count(),
        'total_comments': Comment.objects.filter(is_active=True).count(),
        'total_admins': User.objects.filter(is_superuser=True).count(),
        'total_moderators': User.objects.filter(is_staff=True, is_superuser=False).count(),
        'daily_registrations': fill_dates(daily_registrations),
        'daily_posts': fill_dates(daily_posts),
        'daily_comments': fill_dates(daily_comments),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_users_view(request):
    if not request.user.is_staff:
        return Response({'error': 'Доступ запрещён'}, status=403)

    search = request.query_params.get('search', '')
    role = request.query_params.get('role', '')
    page = request.query_params.get('page', 1)

    users = User.objects.all()

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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_ban_view(request, user_id):
    if not request.user.is_superuser:
        return Response({'error': 'Только администратор может блокировать пользователей'}, status=403)

    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'Пользователь не найден'}, status=404)

    if target_user == request.user:
        return Response({'error': 'Нельзя заблокировать себя'}, status=400)

    if target_user.is_superuser:
        return Response({'error': 'Нельзя заблокировать администратора'}, status=400)

    target_user.is_active = not target_user.is_active
    target_user.save(update_fields=['is_active'])

    return Response({
        'success': True,
        'user_id': target_user.id,
        'username': target_user.username,
        'is_active': target_user.is_active,
    })
