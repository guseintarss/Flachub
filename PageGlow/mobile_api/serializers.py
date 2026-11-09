from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Q
from main.models import (
    Post, Category, TagPost, Comment, 
    Notification, Bookmark, Collection, 
    UserBadge, UserAchievement, Subscription,
    Chat, Message
)

User = get_user_model()


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

    class Meta:
        model = Post
        fields = ('id', 'title', 'slug', 'photo', 'post_type', 'time_create',
                  'time_update', 'author', 'category', 'likes_count', 
                  'favorites_count', 'comments_count', 'is_liked', 
                  'is_favorited', 'reading_time_minutes', 'views', 'excerpt',
                  'code_language', 'review_status')

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
                  'can_claim_review', 'can_release_review')

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


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'slug', 'title', 'content', 'photo', 'post_type', 'is_published',
                  'cat', 'tags', 'code_snippet', 'code_language', 'review_focus')
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
