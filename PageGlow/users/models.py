from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Sum


class UserLevel(models.Model):
    """Уровни пользователей системы репутации"""
    name = models.CharField(max_length=50, verbose_name='Название уровня')
    slug = models.SlugField(unique=True, verbose_name='Слаг')
    min_reputation = models.IntegerField(verbose_name='Минимальная репутация')
    icon = models.CharField(max_length=50, default='🌱', verbose_name='Иконка (emoji)')
    color = models.CharField(max_length=20, default='#999999', verbose_name='Цвет')
    description = models.TextField(blank=True, verbose_name='Описание')
    
    # Привилегии
    can_create_tags = models.BooleanField(default=False, verbose_name='Создание тегов')
    can_edit_own_posts_longer = models.BooleanField(default=False, verbose_name='Расширенное редактирование постов')
    can_moderate_comments = models.BooleanField(default=False, verbose_name='Модерация комментариев')
    daily_upload_limit = models.IntegerField(default=10, verbose_name='Дневной лимит загрузок')
    
    # Автоматический бейдж при получении уровня
    auto_badge = models.ForeignKey(
        'main.UserBadge',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_levels',
        verbose_name='Автоматический бейдж'
    )
    
    class Meta:
        verbose_name = 'Уровень пользователя'
        verbose_name_plural = 'Уровни пользователей'
        ordering = ['min_reputation']
        indexes = [
            models.Index(fields=['min_reputation']),
        ]

    def __str__(self):
        return f'{self.name} (от {self.min_reputation})'


class UserReputationLog(models.Model):
    """История изменений репутации пользователя"""
    class ReasonType(models.TextChoices):
        POST_CREATED = 'post_created', 'Публикация поста'
        POST_LIKED = 'post_liked', 'Лайк поста (автору)'
        COMMENT_CREATED = 'comment_created', 'Создание комментария'
        COMMENT_LIKED = 'comment_liked', 'Лайк комментария (автору)'
        DISCUSSION_CREATED = 'discussion_created', 'Создание обсуждения'
        ANSWER_ACCEPTED = 'answer_accepted', 'Лучший ответ'
        SUBSCRIPTION_RECEIVED = 'subscription_received', 'Подписка на автора'
        PENALTY = 'penalty', 'Штраф (нарушение)'
        MANUAL = 'manual', 'Ручное изменение'

    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='reputation_logs',
        verbose_name='Пользователь'
    )
    amount = models.IntegerField(verbose_name='Изменение репутации')
    reason = models.CharField(
        max_length=50,
        choices=ReasonType.choices,
        verbose_name='Причина'
    )
    post = models.ForeignKey(
        'main.Post',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='reputation_logs',
        verbose_name='Пост'
    )
    comment = models.ForeignKey(
        'main.Comment',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='reputation_logs',
        verbose_name='Комментарий'
    )
    discussion = models.ForeignKey(
        'main.Discussion',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='reputation_logs',
        verbose_name='Обсуждение'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Лог репутации'
        verbose_name_plural = 'Логи репутации'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['reason']),
        ]

    def __str__(self):
        sign = '+' if self.amount > 0 else ''
        return f'{self.user.username}: {sign}{self.amount} ({self.get_reason_display()})'


class User(AbstractUser):
    photo = models.ImageField(upload_to='users/%Y/%m/%d/', null=True, blank=True, verbose_name='Фотография')
    data_birth = models.DateTimeField(null=True, blank=True, verbose_name='Дата рождения')
    phone_namber = models.CharField(max_length=18, null=True, blank=True, verbose_name='Номер телефона' )
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

    # ===== Методы системы репутации =====
    
    @property
    def reputation(self):
        """
        Общая репутация пользователя (кэшируемая)
        """
        cache_key = f'user_reputation_{self.id}'
        rep = cache.get(cache_key)
        if rep is None:
            rep = self.reputation_logs.aggregate(
                total=Sum('amount')
            )['total'] or 0
            cache.set(cache_key, rep, 3600)  # Кэш на 1 час
        return rep

    @property
    def current_level(self):
        """
        Текущий уровень пользователя
        """
        # Кэшируем уровни чтобы избежать повторных запросов
        if not hasattr(self, '_levels_cache'):
            self._levels_cache = list(UserLevel.objects.all().order_by('min_reputation'))
        
        # Находим последний уровень где min_reputation <= reputation
        current = None
        for level in self._levels_cache:
            if level.min_reputation <= self.reputation:
                current = level
            else:
                break
        return current

    @property
    def next_level(self):
        """
        Следующий уровень пользователя
        """
        # Кэшируем уровни если ещё не закэшировано
        if not hasattr(self, '_levels_cache'):
            self._levels_cache = list(UserLevel.objects.all().order_by('min_reputation'))
        
        # Находим первый уровень где min_reputation > reputation
        for level in self._levels_cache:
            if level.min_reputation > self.reputation:
                return level
        return None

    @property
    def level_progress(self):
        """
        Прогресс до следующего уровня (0-100%)
        """
        if not self.current_level or not self.next_level:
            return 100
        
        current_min = self.current_level.min_reputation
        next_min = self.next_level.min_reputation
        range_len = next_min - current_min
        
        if range_len <= 0:
            return 100
        
        progress = ((self.reputation - current_min) / range_len) * 100
        return min(100, max(0, int(progress)))

    @property
    def reputation_today(self):
        """
        Репутация, полученная сегодня (для лимитов)
        """
        from django.utils import timezone
        today = timezone.now().date()
        return self.reputation_logs.filter(
            created_at__date=today
        ).aggregate(total=Sum('amount'))['total'] or 0

    def add_reputation(self, amount, reason, post=None, comment=None, discussion=None):
        """
        Добавить репутацию пользователю с созданием лога
        
        Args:
            amount: Количество репутации (+ или -)
            reason: Причина (из UserReputationLog.ReasonType)
            post: Связанный пост (опционально)
            comment: Связанный комментарий (опционально)
            discussion: Связанное обсуждение (опционально)
        """
        from django.db import transaction
        from main.models import Notification
        
        with transaction.atomic():
            # Создаём лог
            UserReputationLog.objects.create(
                user=self,
                amount=amount,
                reason=reason,
                post=post,
                comment=comment,
                discussion=discussion
            )
            
            # Проверка нового уровня
            old_level = UserLevel.objects.filter(
                min_reputation__lte=self.reputation - amount
            ).order_by('min_reputation').last()
            
            new_level = self.current_level
            
            if new_level and old_level != new_level:
                # Уведомление о новом уровне
                Notification.objects.create(
                    recipient=self,
                    notification_type='achievement',
                    message=f'Вы получили уровень "{new_level.name}"!'
                )
                
                # Выдача бейджа
                if new_level.auto_badge:
                    from main.models import UserAchievement
                    UserAchievement.objects.get_or_create(
                        user=self,
                        badge=new_level.auto_badge,
                        defaults={'reason': f'Уровень {new_level.name}'}
                    )
        
        # Очистка кэша репутации
        cache.delete(f'user_reputation_{self.id}')

    def can_perform_action(self, action_type):
        """
        Проверка, может ли пользователь выполнить действие на основе уровня
        
        Args:
            action_type: Тип действия ('create_tags', 'edit_posts_long', 'moderate_comments')
        
        Returns:
            bool: Доступно ли действие
        """
        level = self.current_level
        if not level:
            return False
        
        action_map = {
            'create_tags': level.can_create_tags,
            'edit_posts_long': level.can_edit_own_posts_longer,
            'moderate_comments': level.can_moderate_comments,
        }
        return action_map.get(action_type, False)

    def get_daily_upload_limit(self):
        """
        Получить дневной лимит загрузок для пользователя
        """
        level = self.current_level
        if not level:
            return 10  # Лимит по умолчанию
        return level.daily_upload_limit


class Rule(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.key