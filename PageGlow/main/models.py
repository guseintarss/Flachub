from django.contrib.auth import get_user_model
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from meta.models import ModelMeta

from users.models import User


def translist_to_eng(s: str) -> str:
    d = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
         'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i', 'к': 'k',
         'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
         'с': 's', 'т': 't', 'у':'u', 'ф': 'f', 'х':'h', 'ц': 'c', 'ч': 'ch',
         'ш': 'sh', 'щ': 'shch', 'ь': '', 'ы': 'y', 'ъ': '', 'э': 'r', 'ю': 'yu', 'я': 'ya'}
    return "".join(map(lambda x: d[x] if d.get(x, False) else x, s.lower()))

class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=Post.Status.PUBLISHED)

class Post(ModelMeta, models.Model):
    class Status(models.IntegerChoices):
        DRAFT = 0, 'Черновик'
        PUBLISHED = 1,'Опубликовано'

    class PostType(models.TextChoices):
        POST = 'post', 'Пост'
        ARTICLE = 'article', 'Статья'
        NEWS = 'news', 'Новость'
        IDEA = 'idea', 'Идея'

    title = models.CharField(max_length=255, verbose_name='Заголовок')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name='slug')
    photo = models.ImageField(upload_to='photos/%Y/%m/%d/', default=None, blank=True, null=True, verbose_name='Фото')
    content = CKEditor5Field(blank=True, config_name='default', verbose_name='Контент')
    post_type = models.CharField(max_length=20, choices=PostType.choices, default=PostType.POST, verbose_name='Тип поста')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    time_update = models.DateTimeField(auto_now=True, verbose_name='Время изменения')
    is_published = models.BooleanField(choices=tuple(map(lambda x: (bool(x[0]), x[1]), Status.choices)), default=Status.DRAFT, verbose_name='Опубликовать?')
    cat = models.ForeignKey('Category', on_delete=models.PROTECT, related_name='posts', verbose_name='Категории')
    tags = models.ManyToManyField('TagPost', blank=True, related_name='tags', verbose_name='Теги')
    author = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, related_name='posts', null=True, default=None)
    
    likes = models.ManyToManyField(
        User,
        related_name='post_likes',
        blank=True
    )

    # Избранное
    favorites = models.ManyToManyField(
        User,
        related_name='favorited_posts',
        blank=True
    )

    # Просмотры
    views = models.PositiveIntegerField(default=0, verbose_name='Просмотры')

    def number_of_likes(self):
        return self.likes.count()

    def number_of_favorites(self):
        return self.favorites.count()

    def reading_time(self):
        """Расчёт времени чтения (средняя скорость 200 слов/мин)"""
        import re
        text = re.sub(r'<[^>]+>', '', self.content or '')
        word_count = len(text.split())
        minutes = max(1, round(word_count / 200))
        return minutes

    def get_similar_posts(self, limit=4):
        """Получить похожие статьи по тегам и категории"""
        # Оптимизация: prefetch_related для уменьшения количества запросов
        post_tags_ids = list(self.tags.values_list('id', flat=True))
        similar_posts = Post.published.select_related('cat', 'author').prefetch_related('tags').filter(
            models.Q(tags__in=post_tags_ids) | models.Q(cat=self.cat)
        ).exclude(id=self.id).distinct()
        return similar_posts.order_by('-views', '-time_create')[:limit]
    

    objects = models.Manager()
    published = PublishedManager()

    _metadata = {
        'title': 'get_meta_title',
        'description': 'get_meta_description',
        'keywords': 'get_keywords_list',
        'image': 'get_image_full_url',
        'og_type': 'article',
        'published_time': 'get_published_time',
        'modified_time': 'get_modified_time',
        'author': 'get_author_name',
        'section': 'get_category_name',
        'tags': 'get_tags_list',
    }

    def get_meta_title(self):
        """Оптимизированный meta title"""
        return f'{self.title} | PageGlow'

    def get_meta_description(self):
        """Оптимизированный meta description (150-160 символов)"""
        if self.content:
            # Удаляем HTML теги
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(self.content, 'html.parser')
            text = soup.get_text()[:200]
            # Очищаем до последнего полного предложения
            if len(text) >= 150:
                text = text.rsplit('.', 1)[0] + '.'
            return text.strip()
        return f'Читайте статью: {self.title}'

    def get_keywords_list(self):
        """Список ключевых слов из тегов"""
        return [tag.tag for tag in self.tags.all()]

    def get_image_full_url(self):
        """Полный URL изображения для OG"""
        if self.photo:
            return self.photo.url
        return '/static/images/og-default.jpg'

    def get_published_time(self):
        """Время публикации в формате ISO 8601"""
        return self.time_create.isoformat()

    def get_modified_time(self):
        """Время изменения в формате ISO 8601"""
        return self.time_update.isoformat()

    def get_author_name(self):
        """Имя автора"""
        return self.author.username if self.author else 'PageGlow'

    def get_category_name(self):
        """Название категории"""
        return self.cat.name if self.cat else 'Блог'

    def get_tags_list(self):
        """Список тегов для OG"""
        return [tag.tag for tag in self.tags.all()]


    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-time_create']
        indexes = [
            models.Index(fields=['-time_create']),
            models.Index(fields=['slug']),
            models.Index(fields=['is_published', '-time_create']),
            models.Index(fields=['author']),
            models.Index(fields=['cat']),
        ]

    def get_absolute_url(self):
        return reverse('post', kwargs={'post_slug': self.slug})

    def save(self, *args, **kwargs):
        key = make_template_fragment_key("side_cache")
        cache.delete(key)
        self.slug = slugify(translist_to_eng(self.title))
        super().save(*args, **kwargs)


class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name='Категория')
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(translist_to_eng(self.name))
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('category', kwargs={'cat_slug': self.slug})

class TagPost(models.Model):
    tag = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)


    def __str__(self):
        return self.tag

    def get_absolute_url(self):
        return reverse('tag', kwargs={'tag_slug': self.slug})

    def save(self, *args, **kwargs):
        key = make_template_fragment_key("side_cache")
        cache.delete(key)

        super().save(*args, **kwargs)

class UploadFiles(models.Model):
    file = models.FileField(upload_to='uploads_model')

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    likes = models.ManyToManyField(User, related_name='comment_likes', blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post', 'created_at']),
            models.Index(fields=['author']),
            models.Index(fields=['is_active']),
            models.Index(fields=['parent']),
        ]

    def __str__(self):
        return f'Comment by {self.author} on {self.post}'
    
    def number_of_likes(self):
        return self.likes.count()
    
    def user_has_liked(self, user):
        if not user or not user.is_authenticated:
            return False
        return self.likes.filter(id=user.id).exists()


class Subscription(models.Model):
    """Подписки на авторов"""
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscribers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('subscriber', 'author')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        indexes = [
            models.Index(fields=['subscriber', 'author']),
            models.Index(fields=['subscriber']),
            models.Index(fields=['author']),
        ]

    def __str__(self):
        return f'{self.subscriber} подписан на {self.author}'


class Notification(models.Model):
    """Уведомления"""
    class NotificationType(models.TextChoices):
        LIKE = 'like', 'Лайк'
        COMMENT = 'comment', 'Комментарий'
        FOLLOW = 'follow', 'Подписка'
        NEW_POST = 'new_post', 'Новая статья'
        ACHIEVEMENT = 'achievement', 'Достижение'

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', null=True)
    notification_type = models.CharField(max_length=20, choices=NotificationType.choices)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['recipient', 'created_at']),
            models.Index(fields=['sender']),
        ]

    def __str__(self):
        return f'{self.notification_type}: {self.message}'


class Discussion(models.Model):
    """Модель обсуждения (вопрос/тема)"""
    class Status(models.IntegerChoices):
        DRAFT = 0, 'Черновик'
        PUBLISHED = 1, 'Опубликовано'
        CLOSED = 2, 'Закрыто'

    title = models.CharField(max_length=255, verbose_name='Заголовок темы', default='', blank=True)
    content = models.TextField(max_length=2000, verbose_name='Описание вопроса', default='', blank=True)
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='discussions',
        verbose_name='Автор',
        null=True,
        blank=True
    )
    cat = models.ForeignKey(
        'Category', 
        on_delete=models.SET_NULL, 
        related_name='discussions',
        null=True, 
        blank=True,
        verbose_name='Категория'
    )
    tags = models.ManyToManyField(
        'TagPost', 
        blank=True, 
        related_name='discussions',
        verbose_name='Теги'
    )
    is_published = models.BooleanField(
        choices=tuple(map(lambda x: (bool(x[0]), x[1]), Status.choices)),
        default=Status.PUBLISHED,
        verbose_name='Опубликовано?' 
    )
    is_closed = models.BooleanField(default=False, verbose_name='Закрыто')
    views = models.PositiveIntegerField(default=0, verbose_name='Просмотры')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    time_update = models.DateTimeField(auto_now=True, verbose_name='Время изменения')

    # Лайки
    likes = models.ManyToManyField(
        User,
        related_name='discussion_likes',
        blank=True
    )

    # Избранное
    favorites = models.ManyToManyField(
        User,
        related_name='discussion_favorites',
        blank=True
    )

    def number_of_likes(self):
        return self.likes.count()

    def number_of_favorites(self):
        return self.favorites.count()

    class Meta:
        verbose_name = 'Обсуждение'
        verbose_name_plural = 'Обсуждения'
        ordering = ['-time_create']
        indexes = [
            models.Index(fields=['-time_create']),
            models.Index(fields=['is_published', '-time_create']),
            models.Index(fields=['author']),
            models.Index(fields=['cat']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('discussion_detail', kwargs={'pk': self.pk})

    def comments_count(self):
        return self.comments.count()

    def get_last_comment_author(self):
        last_comment = self.comments.order_by('-created_at').first()
        return last_comment.author if last_comment else None


class DiscussionComment(models.Model):
    """Комментарий к обсуждению"""
    discussion = models.ForeignKey(
        Discussion,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Обсуждение'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='discussion_comments',
        verbose_name='Автор'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name='Родительский комментарий'
    )
    content = models.TextField(max_length=2000, verbose_name='Текст комментария')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    
    # Лайки на комментарий
    likes = models.ManyToManyField(
        User,
        related_name='discussion_comment_likes',
        blank=True
    )

    class Meta:
        verbose_name = 'Комментарий обсуждения'
        verbose_name_plural = 'Комментарии обсуждений'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['discussion', 'created_at']),
            models.Index(fields=['author']),
            models.Index(fields=['is_active']),
            models.Index(fields=['parent']),
        ]

    def __str__(self):
        return f'Comment by {self.author} on {self.discussion}'

    def number_of_likes(self):
        return self.likes.count()

    def user_has_liked(self, user):
        if not user or not user.is_authenticated:
            return False
        return self.likes.filter(id=user.id).exists()

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('discussion_detail', kwargs={'pk': self.discussion.pk})


# ===== SOCIAL FEATURES =====

class Bookmark(models.Model):
    """Закладки пользователей"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookmarks'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='bookmarked_by'
    )
    collection = models.ForeignKey(
        'Collection',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookmarks'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, max_length=500, help_text='Заметка к закладке')

    class Meta:
        verbose_name = 'Закладка'
        verbose_name_plural = 'Закладки'
        ordering = ['-created_at']
        unique_together = ('user', 'post')
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['post']),
        ]

    def __str__(self):
        return f'{self.user.username} → {self.post.title}'


class Collection(models.Model):
    """Коллекции статей (папки для закладок)"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='collections'
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, max_length=500)
    is_public = models.BooleanField(default=False, help_text='Показывать коллекцию другим')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Коллекция'
        verbose_name_plural = 'Коллекции'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_public']),
        ]

    def __str__(self):
        return f'{self.name} ({self.user.username})'

    def bookmarks_count(self):
        return self.bookmarks.count()


class UserBadge(models.Model):
    """Достижения пользователей"""
    key = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text='Название иконки (emoji или CSS class)')
    color = models.CharField(max_length=20, default='#007bff', help_text='Цвет бейджа')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text='Порядок отображения')

    class Meta:
        verbose_name = 'Достижение'
        verbose_name_plural = 'Достижения'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    """Полученные пользователем достижения"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='achievements'
    )
    badge = models.ForeignKey(
        UserBadge,
        on_delete=models.CASCADE,
        related_name='awarded_to'
    )
    earned_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True, help_text='Причина получения')

    class Meta:
        verbose_name = 'Полученное достижение'
        verbose_name_plural = 'Полученные достижения'
        ordering = ['-earned_at']
        unique_together = ('user', 'badge')
        indexes = [
            models.Index(fields=['user', '-earned_at']),
        ]

    def __str__(self):
        return f'{self.user.username} → {self.badge.name}'