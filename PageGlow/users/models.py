from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone



class User(AbstractUser):
    photo = models.ImageField(upload_to='users/%Y/%m/%d/', null=True, blank=True, verbose_name='Фотография')
    data_birth = models.DateTimeField(null=True, blank=True, verbose_name='Дата рождения')
    phone_namber = models.CharField(max_length=11, null=True, blank=True, verbose_name='Номер телефона' )
    about_me = models.TextField(max_length=255, null=True, blank=True, verbose_name='О себе')
    
    # Подписки на пользователей (друзья/фолловеры)
    following = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='followers',
        blank=True,
        verbose_name='Подписки на пользователей'
    )
    
    # Временные метки
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
        ]
    
    def get_following_count(self):
        """Количество подписок пользователя (на кого подписан)"""
        return self.following.count()
    
    def get_followers_count(self):
        """Количество подписчиков пользователя (кто подписан на этого пользователя)"""
        return self.followers.count()
    
    def is_following(self, user):
        """Проверить, подписан ли пользователь на другого пользователя"""
        return self.following.filter(id=user.id).exists()
    
    def follow(self, user):
        """Подписаться на пользователя"""
        if user != self and not self.is_following(user):
            self.following.add(user)
    
    def unfollow(self, user):
        """Отписаться от пользователя"""
        self.following.remove(user)
    
    # Для обратной совместимости (aliases)
    def get_subscriptions_count(self):
        """Количество подписок пользователя (DEPRECATED, используйте get_following_count)"""
        return self.get_following_count()
    
    def get_subscribers_count(self):
        """Количество подписчиков пользователя (DEPRECATED, используйте get_followers_count)"""
        return self.get_followers_count()
    
    def is_subscribed_to(self, user):
        """Проверить подписку (DEPRECATED, используйте is_following)"""
        return self.is_following(user)
    
    def subscribe_to(self, user):
        """Подписаться (DEPRECATED, используйте follow)"""
        return self.follow(user)
    
    def unsubscribe_from(self, user):
        """Отписаться (DEPRECATED, используйте unfollow)"""
        return self.unfollow(user)
    
    @property
    def subscriptions(self):
        """Для обратной совместимости"""
        return self.following.all()
    
    @property
    def subscribers(self):
        """Для обратной совместимости"""
        return self.followers.all()

class Rule(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.key