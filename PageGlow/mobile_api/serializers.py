from rest_framework import serializers
from django.contrib.auth import get_user_model
from main.models import (
    Post, Category, TagPost, Comment, 
    Notification, Bookmark, Collection, 
    UserBadge, UserAchievement, Subscription
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

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name',
                  'avatar', 'bio', 'is_staff', 'is_superuser', 'date_joined',
                  'banner_gradient_start', 'banner_gradient_end', 'banner_image')

    def get_avatar(self, obj):
        if obj.photo:
            return obj.photo.url
        return None

    def get_banner_image(self, obj):
        if obj.banner_image:
            return obj.banner_image.url
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

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name',
                  'avatar', 'bio', 'is_staff', 'is_superuser', 'date_joined',
                  'banner_gradient_start', 'banner_gradient_end', 'banner_image',
                  'followers_count', 'following_count', 'reputation',
                  'current_level', 'next_level', 'level_progress')

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
                  'is_favorited', 'reading_time_minutes', 'views', 'excerpt')

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

    class Meta:
        model = Post
        fields = ('id', 'title', 'slug', 'photo', 'content', 'post_type',
                  'is_published',
                  'time_create', 'time_update', 'author', 'category', 'tags',
                  'likes_count', 'favorites_count', 'comments_count', 'comments', 'is_liked',
                  'is_favorited', 'is_subscribed', 'current_user',
                  'reading_time_minutes', 'views', 'similar_posts')

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
        qs = obj.comments.filter(parent=None, is_active=True).select_related('author').prefetch_related('likes')
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


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'slug', 'title', 'content', 'photo', 'post_type', 'is_published', 
                  'cat', 'tags')
        extra_kwargs = {
            'cat': {'required': False, 'allow_null': True},
            'slug': {'required': False},
        }

    def validate(self, attrs):
        if not attrs.get('slug') and attrs.get('title'):
            from main.models import translist_to_eng
            from django.template.defaultfilters import slugify
            attrs['slug'] = slugify(translist_to_eng(attrs['title']))
        return attrs


# ===== Comment Serializers =====

class CommentWithRepliesSerializer(serializers.ModelSerializer):
    author = UserPublicSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'author', 'parent', 'content', 'created_at',
                  'likes_count', 'is_liked', 'replies')

    def get_likes_count(self, obj):
        return obj.number_of_likes()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user_has_liked(request.user)
        return False

    def get_replies(self, obj):
        replies = obj.replies.filter(is_active=True).select_related('author').prefetch_related('likes')
        return CommentWithRepliesSerializer(replies, many=True, context=self.context).data


class CommentSerializer(serializers.ModelSerializer):
    author = UserPublicSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    replies_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'post', 'author', 'parent', 'content', 'created_at',
                  'updated_at', 'is_edited', 'likes_count', 'is_liked', 
                  'replies_count')
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
        fields = ('content', 'parent')

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("Комментарий не может быть пустым")
        return value


# ===== Notification Serializers =====

class NotificationSerializer(serializers.ModelSerializer):
    sender = UserPublicSerializer(read_only=True)
    post_title = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ('id', 'sender', 'notification_type', 'post', 'post_title',
                  'message', 'is_read', 'created_at')

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
