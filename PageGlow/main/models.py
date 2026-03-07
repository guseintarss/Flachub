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

    title = models.CharField(max_length=255, verbose_name='Заголовок')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name='slug')
    photo = models.ImageField(upload_to='photos/%Y/%m/%d/', default=None, blank=True, null=True, verbose_name='Фото')
    content = CKEditor5Field(blank=True, config_name='default', verbose_name='Контент')
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
        post_tags_ids = self.tags.values_list('id', flat=True)
        similar_posts = Post.published.filter(
            models.Q(tags__in=post_tags_ids) | models.Q(cat=self.cat)
        ).exclude(id=self.id).distinct()
        return similar_posts.order_by('-views', '-time_create')[:limit]
    

    objects = models.Manager()
    published = PublishedManager()

    _metadata = {
        'title': 'title',
        'description': 'get_meta_description',
        'keywords': 'get_keywords_list',
        'image': 'get_image_full_url',
    }

    def get_meta_title(self):
        return f'{self.title}'

    def get_meta_description(self):
        return f'{self.content[:200]}...'

    def get_keywords_list(self):
        return [tag.name for tag in self.tags.all()]

    def get_image_full_url(self):
        if self.photo:
            return self.photo.url
        return None


    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-time_create']
        indexes = [
            models.Index(fields=['-time_create']),
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
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Comment by {self.author} on {self.post}'


class Subscription(models.Model):
    """Подписки на авторов"""
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscribers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('subscriber', 'author')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.subscriber} подписан на {self.author}'


class Notification(models.Model):
    """Уведомления"""
    class NotificationType(models.TextChoices):
        LIKE = 'like', 'Лайк'
        COMMENT = 'comment', 'Комментарий'
        FOLLOW = 'follow', 'Подписка'
        NEW_POST = 'new_post', 'Новая статья'

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

    def __str__(self):
        return f'{self.notification_type}: {self.message}'

