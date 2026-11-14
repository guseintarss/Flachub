from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from main.models import (
    Post, Category, TagPost, Comment, 
    Notification, Bookmark, Collection, 
    UserBadge, UserAchievement, Subscription,
    Chat, Message, ReviewRequest, ReviewOffer
)

User = get_user_model()

_MISSING = object()


class BlankableDateTimeField(serializers.DateTimeField):
    """Пустая строка из FormData очищает дедлайн."""

    def to_internal_value(self, value):
        if value in ('', None):
            return None
        return super().to_internal_value(value)


class BlankableIntegerField(serializers.IntegerField):
    """Пустая строка из FormData очищает бюджет."""

    def to_internal_value(self, value):
        if value in ('', None):
            return None
        return super().to_internal_value(value)


# ===== User Serializers =====

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                  'date_joined', 'avatar', 'bio')
        read_only_fields = ('date_joined',)


class UserPublicSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    bio = serializers.CharField(source='about_me', read_only=True)
    banner_image = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    birth_date = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()
    reputation = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name',
                  'avatar', 'bio', 'is_staff', 'is_superuser', 'is_active', 'date_joined',
                  'banner_gradient_start', 'banner_gradient_end', 'banner_image',
                  'phone', 'birth_date', 'posts_count', 'reputation')

    def get_reputation(self, obj):
        return obj.reputation

    def get_posts_count(self, obj):
        return getattr(obj, 'posts_count', None) or 0

    def get_avatar(self, obj):
        if obj.photo:
            return obj.photo.url
        return None

    def get_banner_image(self, obj):
        if obj.banner_image:
            return obj.banner_image.url
        return None

    def get_email(self, obj):
        if obj.show_email:
            return obj.email
        return None

    def get_phone(self, obj):
        if obj.show_phone and obj.phone_namber:
            return obj.phone_namber
        return None

    def get_birth_date(self, obj):
        if obj.show_birth_date and obj.data_birth:
            return obj.data_birth.date().isoformat()
        return None


class UserProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    bio = serializers.CharField(source='about_me', read_only=True)
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    reputation = serializers.SerializerMethodField()
    current_level = serializers.SerializerMethodField()
    next_level = serializers.SerializerMethodField()
    level_progress = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    phone_namber = serializers.SerializerMethodField()
    data_birth = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name',
                  'avatar', 'bio', 'is_staff', 'is_superuser', 'date_joined',
                  'banner_gradient_start', 'banner_gradient_end', 'banner_image',
                  'followers_count', 'following_count', 'reputation',
                  'current_level', 'next_level', 'level_progress',
                  'show_email', 'show_phone', 'show_birth_date',
                  'phone_namber', 'data_birth')

    def get_avatar(self, obj):
        if obj.photo:
            return obj.photo.url
        return None

    def get_banner_image(self, obj):
        if obj.banner_image:
            return obj.banner_image.url
        return None

    def get_followers_count(self, obj):
        return Subscription.objects.filter(author=obj).count()

    def get_following_count(self, obj):
        return Subscription.objects.filter(subscriber=obj).count()

    def get_reputation(self, obj):
        return obj.reputation

    def get_current_level(self, obj):
        level = obj.current_level
        if not level:
            return None
        return {
            'name': level.name,
            'slug': level.slug,
            'min_reputation': level.min_reputation,
            'icon': level.icon,
            'color': level.color,
        }

    def get_next_level(self, obj):
        level = obj.next_level
        if not level:
            return None
        return {
            'name': level.name,
            'slug': level.slug,
            'min_reputation': level.min_reputation,
            'icon': level.icon,
            'color': level.color,
        }

    def get_level_progress(self, obj):
        return obj.level_progress

    def get_email(self, obj):
        if obj.show_email:
            return obj.email
        return None

    def get_phone_namber(self, obj):
        if obj.show_phone and obj.phone_namber:
            return obj.phone_namber
        return None

    def get_data_birth(self, obj):
        if obj.show_birth_date and obj.data_birth:
            return obj.data_birth.date().isoformat()
        return None


# ===== Category & Tag Serializers =====

class CategorySerializer(serializers.ModelSerializer):
    posts_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'posts_count')

    def get_posts_count(self, obj):
        return obj.posts.filter(is_published=Post.Status.PUBLISHED).count()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagPost
        fields = ('id', 'tag', 'slug')


# ===== Post Serializers =====

class PostListSerializer(serializers.ModelSerializer):
    author = UserPublicSerializer(read_only=True)
    category = CategorySerializer(source='cat', read_only=True)
    likes_count = serializers.SerializerMethodField()
    favorites_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    reading_time_minutes = serializers.SerializerMethodField()
    excerpt = serializers.SerializerMethodField()
    review_deadline = serializers.SerializerMethodField()
    review_budget = serializers.SerializerMethodField()
    review_offers_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'title', 'slug', 'photo', 'post_type', 'time_create',
                  'time_update', 'author', 'category', 'likes_count', 
                  'favorites_count', 'comments_count', 'is_liked', 
                  'is_favorited', 'reading_time_minutes', 'views', 'excerpt',
                  'code_language', 'review_status', 'review_focus',
                  'review_deadline', 'review_budget', 'review_offers_count')

    def get_likes_count(self, obj):
        if hasattr(obj, 'likes_count'):
            return obj.likes_count
        return obj.number_of_likes()

    def get_favorites_count(self, obj):
        if hasattr(obj, 'favorites_count'):
            return obj.favorites_count
        return obj.number_of_favorites()

    def get_comments_count(self, obj):
        return obj.comments.filter(is_active=True).count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorites.filter(id=request.user.id).exists()
        return False

    def get_reading_time_minutes(self, obj):
        return obj.reading_time()

    def get_excerpt(self, obj):
        import re
        text = re.sub(r'<[^>]+>', '', obj.content or '')
        words = text.split()
        if len(words) > 40:
            return ' '.join(words[:40]) + '...'
        return text

    def _review_request(self, obj):
        return getattr(obj, 'review_request', None)

    def get_review_deadline(self, obj):
        review_request = self._review_request(obj)
        return review_request.deadline.isoformat() if review_request and review_request.deadline else None

    def get_review_budget(self, obj):
        review_request = self._review_request(obj)
        return review_request.budget if review_request else None

    def get_review_offers_count(self, obj):
        review_request = self._review_request(obj)
        if not review_request:
            return 0
        if not hasattr(review_request, '_pending_offers_count'):
            review_request._pending_offers_count = review_request.offers.filter(
                status=ReviewOffer.Status.PENDING
            ).count()
        return review_request._pending_offers_count


class ReviewOfferSerializer(serializers.ModelSerializer):
    reviewer = UserPublicSerializer(read_only=True)
    can_withdraw = serializers.SerializerMethodField()

    class Meta:
        model = ReviewOffer
        fields = ('id', 'reviewer', 'message', 'price', 'deadline_days',
                  'status', 'created_at', 'can_withdraw')

    def get_can_withdraw(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        return bool(
            user
            and user.is_authenticated
            and obj.reviewer_id == user.id
            and obj.status == ReviewOffer.Status.PENDING
            and obj.request.status == ReviewRequest.Status.OPEN
        )


class ReviewRequestPostSerializer(serializers.ModelSerializer):
    author = UserPublicSerializer(read_only=True)
    category = CategorySerializer(source='cat', read_only=True)
    comments_count = serializers.SerializerMethodField()
    excerpt = serializers.SerializerMethodField()
    code_preview = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'title', 'slug', 'photo', 'post_type', 'time_create',
                  'author', 'category', 'comments_count', 'views', 'excerpt',
                  'code_language', 'review_focus', 'review_status', 'code_preview')

    def get_comments_count(self, obj):
        return obj.comments.filter(is_active=True).count()

    def get_excerpt(self, obj):
        import re
        text = re.sub(r'<[^>]+>', '', obj.content or '')
        words = text.split()
        return ' '.join(words[:30]) + ('...' if len(words) > 30 else '')

    def get_code_preview(self, obj):
        lines = (obj.code_snippet or '').splitlines()[:8]
        return '\n'.join(lines)


class ReviewRequestSerializer(serializers.ModelSerializer):
    post = ReviewRequestPostSerializer(read_only=True)
    selected_offer = ReviewOfferSerializer(read_only=True)
    offers = serializers.SerializerMethodField()
    offers_count = serializers.SerializerMethodField()
    my_offer = serializers.SerializerMethodField()
    can_offer = serializers.SerializerMethodField()
    can_select_offer = serializers.SerializerMethodField()
    can_cancel = serializers.SerializerMethodField()

    class Meta:
        model = ReviewRequest
        fields = ('id', 'post', 'deadline', 'budget', 'status',
                  'selected_offer', 'offers', 'offers_count', 'my_offer',
                  'can_offer', 'can_select_offer', 'can_cancel',
                  'created_at', 'updated_at')

    def _user(self):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        return user if user and user.is_authenticated else None

    def _is_author(self, obj):
        user = self._user()
        return bool(user and (obj.post.author_id == user.id or user.is_staff))

    def get_offers(self, obj):
        user = self._user()
        if not user:
            return []
        queryset = obj.offers.select_related('reviewer')
        if self._is_author(obj):
            queryset = queryset.exclude(status=ReviewOffer.Status.WITHDRAWN)
        else:
            queryset = queryset.filter(reviewer=user)
        return ReviewOfferSerializer(queryset, many=True, context=self.context).data

    def get_offers_count(self, obj):
        if not hasattr(obj, '_pending_offers_count'):
            obj._pending_offers_count = obj.offers.filter(
                status=ReviewOffer.Status.PENDING
            ).count()
        return obj._pending_offers_count

    def get_my_offer(self, obj):
        user = self._user()
        if not user:
            return None
        offer = obj.offers.filter(reviewer=user).first()
        return ReviewOfferSerializer(offer, context=self.context).data if offer else None

    def get_can_offer(self, obj):
        user = self._user()
        return bool(
            user
            and obj.post.author_id != user.id
            and obj.post.is_published
            and obj.status == ReviewRequest.Status.OPEN
            and obj.post.review_status == Post.ReviewStatus.OPEN
            and (obj.deadline is None or obj.deadline > timezone.now())
        )

    def get_can_select_offer(self, obj):
        return bool(
            self._is_author(obj)
            and obj.status == ReviewRequest.Status.OPEN
            and obj.offers.filter(status=ReviewOffer.Status.PENDING).exists()
        )

    def get_can_cancel(self, obj):
        return bool(
            self._is_author(obj)
            and obj.status in (ReviewRequest.Status.OPEN, ReviewRequest.Status.IN_REVIEW)
        )


class PostDetailSerializer(serializers.ModelSerializer):
    author = UserPublicSerializer(read_only=True)
    reviewer = UserPublicSerializer(read_only=True)
    category = CategorySerializer(source='cat', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    favorites_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    current_user = serializers.SerializerMethodField()
    reading_time_minutes = serializers.SerializerMethodField()
    similar_posts = serializers.SerializerMethodField()
    is_review_author = serializers.SerializerMethodField()
    can_claim_review = serializers.SerializerMethodField()
    can_release_review = serializers.SerializerMethodField()
    review_request = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'title', 'slug', 'photo', 'content', 'post_type',
                  'is_published',
                  'time_create', 'time_update', 'author', 'category', 'tags',
                  'likes_count', 'favorites_count', 'comments_count', 'comments', 'is_liked',
                  'is_favorited', 'is_subscribed', 'current_user',
                  'reading_time_minutes', 'views', 'similar_posts',
                  'code_snippet', 'code_language', 'review_focus', 'review_status',
                  'reviewer', 'review_accepted_at', 'is_review_author',
                  'can_claim_review', 'can_release_review', 'review_request')

    def get_likes_count(self, obj):
        if hasattr(obj, 'likes_count'):
            return obj.likes_count
        return obj.number_of_likes()

    def get_favorites_count(self, obj):
        if hasattr(obj, 'favorites_count'):
            return obj.favorites_count
        return obj.number_of_favorites()

    def get_comments_count(self, obj):
        return obj.comments.filter(is_active=True).count()

    def get_comments(self, obj):
        qs = obj.comments.filter(parent=None, is_active=True).select_related('author', 'post').prefetch_related('likes')
        return CommentWithRepliesSerializer(qs, many=True, context=self.context).data

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorites.filter(id=request.user.id).exists()
        return False

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated and obj.author:
            return Subscription.objects.filter(
                subscriber=request.user,
                author=obj.author
            ).exists()
        return False

    def get_current_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.username
        return None

    def get_reading_time_minutes(self, obj):
        return obj.reading_time()

    def get_similar_posts(self, obj):
        similar = obj.get_similar_posts(limit=4)
        return PostListSerializer(similar, many=True, context=self.context).data

    def get_is_review_author(self, obj):
        request = self.context.get('request')
        return bool(
            request and request.user.is_authenticated
            and obj.author_id == request.user.id
        )

    def get_can_claim_review(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return (
            obj.post_type == Post.PostType.REVIEW
            and obj.is_published == Post.Status.PUBLISHED
            and obj.review_status == Post.ReviewStatus.OPEN
            and obj.author_id != request.user.id
        )

    def get_can_release_review(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return (
            obj.review_status == Post.ReviewStatus.IN_REVIEW
            and (obj.reviewer_id == request.user.id or request.user.is_staff)
        )

    def get_review_request(self, obj):
        review_request = getattr(obj, 'review_request', None)
        if not review_request:
            return None
        return ReviewRequestSerializer(review_request, context=self.context).data


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    review_deadline = BlankableDateTimeField(
        required=False, allow_null=True, write_only=True,
    )
    review_budget = BlankableIntegerField(
        required=False, allow_null=True, min_value=0, max_value=10_000_000,
        write_only=True,
    )

    class Meta:
        model = Post
        fields = ('id', 'slug', 'title', 'content', 'photo', 'post_type', 'is_published',
                  'cat', 'tags', 'code_snippet', 'code_language', 'review_focus',
                  'review_deadline', 'review_budget')
        read_only_fields = ('slug',)
        extra_kwargs = {
            'cat': {'required': False, 'allow_null': True},
        }

    def validate(self, attrs):
        instance = self.instance
        post_type = attrs.get(
            'post_type',
            instance.post_type if instance else Post.PostType.POST,
        )

        if post_type == Post.PostType.REVIEW:
            code_snippet = attrs.get(
                'code_snippet',
                instance.code_snippet if instance else '',
            )
            code_language = attrs.get(
                'code_language',
                instance.code_language if instance else '',
            )
            errors = {}
            if not (code_snippet or '').strip():
                errors['code_snippet'] = 'Для разбора нужен код'
            if not (code_language or '').strip():
                errors['code_language'] = 'Укажите язык кода'
            deadline = attrs.get('review_deadline', _MISSING)
            if deadline is not _MISSING and deadline is not None and deadline <= timezone.now():
                errors['review_deadline'] = 'Дедлайн должен быть в будущем'
            if errors:
                raise serializers.ValidationError(errors)
        elif instance and instance.post_type == Post.PostType.REVIEW:
            # Смена типа с review на другой: чистим состояние разбора.
            attrs['code_snippet'] = ''
            attrs['code_language'] = ''
            attrs['review_focus'] = ''
            attrs['reviewer'] = None
            attrs['review_status'] = Post.ReviewStatus.OPEN
            attrs['review_accepted_at'] = None

        return attrs

    def _apply_review_request(self, post, deadline=_MISSING, budget=_MISSING):
        if post.post_type != Post.PostType.REVIEW:
            ReviewRequest.objects.filter(post=post).delete()
            return
        review_request, _ = ReviewRequest.objects.get_or_create(post=post)
        update_fields = []
        if deadline is not _MISSING:
            review_request.deadline = deadline
            update_fields.append('deadline')
        if budget is not _MISSING:
            review_request.budget = budget
            update_fields.append('budget')
        if update_fields:
            update_fields.append('updated_at')
            review_request.save(update_fields=update_fields)

    def create(self, validated_data):
        deadline = validated_data.pop('review_deadline', _MISSING)
        budget = validated_data.pop('review_budget', _MISSING)
        post = super().create(validated_data)
        self._apply_review_request(post, deadline, budget)
        return post

    def update(self, instance, validated_data):
        deadline = validated_data.pop('review_deadline', _MISSING)
        budget = validated_data.pop('review_budget', _MISSING)
        post = super().update(instance, validated_data)
        self._apply_review_request(post, deadline, budget)
        return post


# ===== Comment Serializers =====

class CommentReviewFieldsMixin(serializers.Serializer):
    """Общие review-поля и флаги действий для комментариев."""

    can_accept = serializers.SerializerMethodField()
    can_resolve = serializers.SerializerMethodField()

    def get_can_accept(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        post = obj.post
        return bool(
            post.post_type == Post.PostType.REVIEW
            and post.review_status != Post.ReviewStatus.COMPLETED
            and post.author_id == user.id
            and obj.author_id != user.id
            and not obj.is_accepted
        )

    def get_can_resolve(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        return bool(
            obj.line_start is not None
            and (obj.author_id == user.id or obj.post.author_id == user.id)
        )


class CommentWithRepliesSerializer(CommentReviewFieldsMixin, serializers.ModelSerializer):
    author = UserPublicSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'author', 'parent', 'content', 'created_at',
                  'likes_count', 'is_liked', 'replies',
                  'line_start', 'line_end', 'severity', 'is_resolved',
                  'is_accepted', 'can_accept', 'can_resolve')

    def get_likes_count(self, obj):
        return obj.number_of_likes()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user_has_liked(request.user)
        return False

    def get_replies(self, obj):
        replies = obj.replies.filter(is_active=True).select_related('author', 'post').prefetch_related('likes')
        return CommentWithRepliesSerializer(replies, many=True, context=self.context).data


class CommentSerializer(CommentReviewFieldsMixin, serializers.ModelSerializer):
    author = UserPublicSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    replies_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'post', 'author', 'parent', 'content', 'created_at',
                  'updated_at', 'is_edited', 'likes_count', 'is_liked', 
                  'replies_count', 'line_start', 'line_end', 'severity',
                  'is_resolved', 'is_accepted', 'can_accept', 'can_resolve')
        read_only_fields = ('author', 'is_edited')

    def get_likes_count(self, obj):
        return obj.number_of_likes()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user_has_liked(request.user)
        return False

    def get_replies_count(self, obj):
        return obj.replies.filter(is_active=True).count()


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('content', 'parent', 'line_start', 'line_end', 'severity')

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("Комментарий не может быть пустым")
        return value

    def validate(self, attrs):
        instance = self.instance
        post = self.context.get('post')
        if post is None and instance is not None:
            post = instance.post

        line_start = attrs.get(
            'line_start',
            instance.line_start if instance else None,
        )
        line_end = attrs.get(
            'line_end',
            instance.line_end if instance else None,
        )

        if line_start is None:
            if line_end is not None:
                raise serializers.ValidationError(
                    {'line_end': 'Нельзя указать конец строки без начала'}
                )
            return attrs

        if post is None or post.post_type != Post.PostType.REVIEW:
            raise serializers.ValidationError(
                {'line_start': 'Строчные замечания доступны только для разборов'}
            )

        total_lines = len((post.code_snippet or '').splitlines())
        errors = {}
        if line_start < 1 or line_start > total_lines:
            errors['line_start'] = (
                f'Строка должна быть в диапазоне 1–{total_lines}'
            )

        if line_end is None:
            line_end = line_start
            attrs['line_end'] = line_end
        elif line_end < line_start:
            errors['line_end'] = 'Конец строки не может быть раньше начала'
        elif line_end > total_lines:
            errors['line_end'] = (
                f'Строка должна быть в диапазоне 1–{total_lines}'
            )

        if errors:
            raise serializers.ValidationError(errors)
        return attrs


# ===== Notification Serializers =====

class NotificationSerializer(serializers.ModelSerializer):
    sender = UserPublicSerializer(read_only=True)
    post_title = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ('id', 'sender', 'notification_type', 'post', 'post_title',
                  'chat', 'message', 'is_read', 'created_at')

    def get_post_title(self, obj):
        return obj.post.title if obj.post else None


# ===== Bookmark & Collection Serializers =====

class CollectionSerializer(serializers.ModelSerializer):
    bookmarks_count = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = ('id', 'name', 'description', 'is_public', 'created_at',
                  'updated_at', 'bookmarks_count')

    def get_bookmarks_count(self, obj):
        return obj.bookmarks.count()


class BookmarkSerializer(serializers.ModelSerializer):
    post = PostListSerializer(read_only=True)
    collection = CollectionSerializer(read_only=True)

    class Meta:
        model = Bookmark
        fields = ('id', 'post', 'collection', 'created_at', 'notes')


class BookmarkCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ('post', 'collection', 'notes')


# ===== Achievement Serializers =====

class UserBadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBadge
        fields = ('id', 'key', 'name', 'description', 'icon', 'color')


class UserAchievementSerializer(serializers.ModelSerializer):
    badge = UserBadgeSerializer(read_only=True)

    class Meta:
        model = UserAchievement
        fields = ('id', 'badge', 'earned_at', 'reason')


# ===== Chat / Message Serializers =====

class MessageSerializer(serializers.ModelSerializer):
    sender = UserPublicSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'sender', 'text', 'created_at', 'is_read')
        read_only_fields = ('sender', 'is_read')


class ChatListSerializer(serializers.ModelSerializer):
    participants = UserPublicSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ('id', 'participants', 'created_at', 'updated_at',
                  'last_message', 'unread_count')

    def get_last_message(self, obj):
        return {
            'text': obj.last_message,
            'time': obj.last_message_time.isoformat() if obj.last_message_time else None,
            'sender_id': obj.last_message_sender_id,
        }

    def get_unread_count(self, obj):
        user = self.context['request'].user
        return obj.messages.filter(~Q(sender=user), is_read=False).count()


class ChatDetailSerializer(serializers.ModelSerializer):
    participants = UserPublicSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ('id', 'participants', 'created_at', 'updated_at')


class ChatCreateSerializer(serializers.Serializer):
    participant_id = serializers.IntegerField()

    def validate_participant_id(self, value):
        User = get_user_model()
        try:
            User.objects.get(id=value, is_active=True)
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь не найден")
        return value


class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('text',)

    def validate_text(self, value):
        if not value.strip():
            raise serializers.ValidationError("Сообщение не может быть пустым")
        return value
