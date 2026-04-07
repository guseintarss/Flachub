from rest_framework import serializers
from django.contrib.auth import get_user_model
from main.models import (
    Post, Category, TagPost, Comment, 
    Notification, Bookmark, Collection, 
    UserBadge, UserAchievement
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
    class Meta:
        model = User
        fields = ('id', 'username', 'avatar', 'bio')


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

    class Meta:
        model = Post
        fields = ('id', 'title', 'slug', 'photo', 'post_type', 'time_create',
                  'time_update', 'author', 'category', 'likes_count', 
                  'favorites_count', 'comments_count', 'is_liked', 
                  'is_favorited', 'reading_time_minutes', 'views')

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


class PostDetailSerializer(serializers.ModelSerializer):
    author = UserPublicSerializer(read_only=True)
    category = CategorySerializer(source='cat', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    favorites_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    reading_time_minutes = serializers.SerializerMethodField()
    similar_posts = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'title', 'slug', 'photo', 'content', 'post_type',
                  'time_create', 'time_update', 'author', 'category', 'tags',
                  'likes_count', 'favorites_count', 'comments_count', 'is_liked',
                  'is_favorited', 'reading_time_minutes', 'views', 'similar_posts')

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

    def get_similar_posts(self, obj):
        similar = obj.get_similar_posts(limit=4)
        return PostListSerializer(similar, many=True, context=self.context).data


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('title', 'content', 'photo', 'post_type', 'is_published', 
                  'cat', 'tags')

    def validate(self, attrs):
        if not attrs.get('slug') and attrs.get('title'):
            from django.template.defaultfilters import slugify
            attrs['slug'] = slugify(attrs['title'])
        return attrs


# ===== Comment Serializers =====

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
