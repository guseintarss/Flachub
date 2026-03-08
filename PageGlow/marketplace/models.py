from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.db.models import Avg, Count, Q
import uuid

# ===== ENUM CHOICES =====

class ProjectStatus(models.TextChoices):
    DRAFT = 'draft', 'Черновик'
    PUBLISHED = 'published', 'Опубликован'
    IN_PROGRESS = 'in_progress', 'В работе'
    REVIEW = 'review', 'На проверке'
    COMPLETED = 'completed', 'Завершен'
    CANCELLED = 'cancelled', 'Отменён'


class BidStatus(models.TextChoices):
    PENDING = 'pending', 'Ожидает рассмотрения'
    ACCEPTED = 'accepted', 'Принята'
    REJECTED = 'rejected', 'Отклонена'
    WITHDRAWN = 'withdrawn', 'Отозвана'


class PaymentStatus(models.TextChoices):
    PENDING = 'pending', 'Ожидает'
    PROCESSING = 'processing', 'Обрабатывается'
    COMPLETED = 'completed', 'Завершено'
    REFUNDED = 'refunded', 'Возвращено'
    DISPUTED = 'disputed', 'В споре'


class FreelancerRole(models.TextChoices):
    BACKEND = 'backend', 'Backend разработчик'
    FRONTEND = 'frontend', 'Frontend разработчик'
    FULLSTACK = 'fullstack', 'Fullstack разработчик'
    DEVOPS = 'devops', 'DevOps инженер'
    DATA_SCIENTIST = 'data_scientist', 'Data Scientist'
    MOBILE = 'mobile', 'Мобильный разработчик'
    QA = 'qa', 'QA инженер'
    DESIGNER = 'designer', 'UI/UX дизайнер'
    MANAGER = 'manager', 'Проект менеджер'
    OTHER = 'other', 'Другое'


class ExperienceLevel(models.TextChoices):
    JUNIOR = 'junior', 'До 1 года'
    JUNIOR_PLUS = 'junior_plus', 'От 1 до 3 лет'
    MIDDLE = 'middle', 'От 3 до 6 лет'
    SENIOR = 'senior', 'От 6 до 10 лет'
    LEAD = 'lead', 'Более 10 лет'


# ===== SKILL MODELS =====

class SkillCategory(models.TextChoices):
    LANGUAGE = 'language', 'Язык программирования'
    FRAMEWORK = 'framework', 'Фреймворк'
    TOOL = 'tool', 'Инструмент'
    DATABASE = 'database', 'База данных'
    DESIGN = 'design', 'Дизайн'
    MOBILE = 'mobile', 'Мобильная разработка'
    DEVOPS = 'devops', 'DevOps / Infrastructure'
    TESTING = 'testing', 'Тестирование'
    OTHER = 'other', 'Другое'


class Skill(models.Model):
    """Навыки (теги технологий)"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    category = models.CharField(
        max_length=20,
        choices=SkillCategory.choices,
        default=SkillCategory.OTHER
    )
    icon = models.CharField(
        max_length=200,
        blank=True,
        help_text='CSS класс иконки (например: fab fa-python или fas fa-database)'
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        help_text='Краткое описание навыка'
    )
    is_popular = models.BooleanField(
        default=False,
        help_text='Показывать в списке популярных навыков'
    )

    class Meta:
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'
        ordering = ['-is_popular', 'category', 'name']
        indexes = [
            models.Index(fields=['category', 'is_popular']),
        ]

    def __str__(self):
        return self.name


# ===== PROFILE MODELS =====

class FreelancerProfile(models.Model):
    """Расширенный профиль фрилансера"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='freelancer_profile')
    
    # Основная информация
    role = models.CharField(
        max_length=20,
        choices=FreelancerRole.choices,
        default=FreelancerRole.OTHER
    )
    bio = models.TextField(max_length=1000, blank=True, help_text='О себе (максимум 1000 символов)')
    avatar = models.ImageField(upload_to='freelancers/avatars/', null=True, blank=True)
    
    # Опыт
    years_experience = models.CharField(
        max_length=20,
        choices=ExperienceLevel.choices,
        default=ExperienceLevel.JUNIOR,
        help_text='Уровень опыта работы'
    )
    skills = models.ManyToManyField('Skill', related_name='freelancers', blank=True)
    
    # Портфолио
    portfolio_url = models.URLField(blank=True, help_text='Ссылка на портфолио')
    github_url = models.URLField(blank=True, help_text='GitHub профиль')
    linkedin_url = models.URLField(blank=True, help_text='LinkedIn профиль')
    
    # Рейтинг и статистика
    rating = models.FloatField(default=5.0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    total_reviews = models.IntegerField(default=0)
    total_projects = models.IntegerField(default=0)
    total_earned = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Статус
    is_verified = models.BooleanField(default=False, help_text='Проверенный профиль')
    is_available = models.BooleanField(default=True, help_text='Доступен для новых проектов')
    
    # Цены
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text='Почасовая ставка в рублях'
    )
    
    # Временные метки
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Профиль фрилансера'
        verbose_name_plural = 'Профили фрилансеров'
        indexes = [
            models.Index(fields=['is_available', 'rating']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

    def get_completion_rate(self):
        """Процент завершённых проектов"""
        if self.total_projects == 0:
            return 0
        completed = Project.objects.filter(
            assigned_to=self.user,
            status=ProjectStatus.COMPLETED
        ).count()
        return round((completed / self.total_projects) * 100, 1)

    def add_review(self, rating, comment=''):
        """Добавить оценку (вызывается после завершения проекта)"""
        if rating < 1 or rating > 5:
            raise ValueError('Рейтинг должен быть от 1 до 5')
        
        self.total_reviews += 1
        self.rating = (self.rating * (self.total_reviews - 1) + rating) / self.total_reviews
        self.save()


class CompanyProfile(models.Model):
    """Профиль заказчика (компании)"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='company_profile')
    
    company_name = models.CharField(max_length=200)
    company_description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='companies/logos/', null=True, blank=True)
    website = models.URLField(blank=True)
    
    # Рейтинг
    rating = models.FloatField(default=5.0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    total_reviews = models.IntegerField(default=0)
    
    # Статистика
    total_projects = models.IntegerField(default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Профиль компании'
        verbose_name_plural = 'Профили компаний'

    def __str__(self):
        return self.company_name


# ===== PROJECT MODELS =====

class Project(models.Model):
    """Проект/задача на маркетплейсе"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Основная информация
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Требуемые навыки
    required_skills = models.ManyToManyField(Skill, related_name='projects')
    
    # Заказчик
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_projects')
    
    # Бюджет
    budget_min = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(1)])
    budget_max = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(1)])
    budget_type = models.CharField(
        max_length=10,
        choices=[
            ('fixed', 'Фиксированная сумма'),
            ('hourly', 'Почасовая ставка'),
        ],
        default='fixed'
    )
    currency = models.CharField(max_length=3, default='RUB')
    
    # Сроки
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Статус
    status = models.CharField(
        max_length=20,
        choices=ProjectStatus.choices,
        default=ProjectStatus.PUBLISHED
    )
    
    # Назначение
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_projects'
    )
    
    # Бюджет платежа
    budget_remaining = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Теги и категория
    category = models.CharField(
        max_length=50,
        choices=[
            ('web', 'Веб-разработка'),
            ('mobile', 'Мобильное приложение'),
            ('data', 'Data Science'),
            ('devops', 'DevOps'),
            ('design', 'Дизайн'),
            ('other', 'Другое'),
        ],
        default='other'
    )
    
    # Уровень сложности
    difficulty = models.CharField(
        max_length=20,
        choices=[
            ('easy', 'Легко'),
            ('medium', 'Средне'),
            ('hard', 'Сложно'),
        ],
        default='medium'
    )
    
    # Дополнительные параметры
    is_urgent = models.BooleanField(default=False, help_text='Срочный проект')
    attachments = models.JSONField(default=list, blank=True, help_text='Ссылки на файлы/прототипы')
    
    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['client', 'status']),
            models.Index(fields=['deadline']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Автоматически устанавливаем budget_remaining при создании"""
        if not self.pk:
            self.budget_remaining = self.budget_max
        super().save(*args, **kwargs)

    def get_active_bids(self):
        """Получить активные предложения"""
        return self.bids.filter(status=BidStatus.PENDING)

    def ai_matching_score(self, freelancer_user):
        """
        Рассчитать AI-оценку совместимости фрилансера с проектом (0-100)
        """
        score = 0
        freelancer = freelancer_user.freelancer_profile
        
        # 1. Совпадение навыков (40 баллов)
        project_skills = set(self.required_skills.values_list('id', flat=True))
        freelancer_skills = set(freelancer.skills.values_list('id', flat=True))
        
        if project_skills:
            skill_match = len(project_skills & freelancer_skills) / len(project_skills)
            score += skill_match * 40
        else:
            score += 40  # Если нет требований по навыкам, даем полный балл
        
        # 2. Опыт (20 баллов)
        if self.difficulty == 'easy':
            score += 20
        elif self.difficulty == 'medium':
            if freelancer.years_experience >= 1:
                score += 20
            elif freelancer.years_experience >= 0.5:
                score += 15
        elif self.difficulty == 'hard':
            if freelancer.years_experience >= 3:
                score += 20
            elif freelancer.years_experience >= 1:
                score += 15
        
        # 3. Рейтинг (20 баллов)
        rating_score = (freelancer.rating / 5) * 20
        score += rating_score
        
        # 4. Доступность (10 баллов)
        if freelancer.is_available:
            score += 10
        
        # 5. Верификация (10 баллов бонус)
        if freelancer.is_verified:
            score += 10
        
        return min(100, score)  # Максимум 100 баллов


class Bid(models.Model):
    """Предложение на проект"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='bids')
    freelancer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bids')
    
    # Предложение
    proposed_price = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_days = models.IntegerField(validators=[MinValueValidator(1)])
    cover_letter = models.TextField(max_length=2000)
    
    # AI оценка совместимости
    ai_score = models.FloatField(default=0, help_text='AI-оценка совместимости с проектом')
    
    # Статус
    status = models.CharField(
        max_length=20,
        choices=BidStatus.choices,
        default=BidStatus.PENDING
    )
    
    # Временные метки
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Предложение'
        verbose_name_plural = 'Предложения'
        ordering = ['-ai_score', '-created_at']
        unique_together = ['project', 'freelancer']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['project', 'status']),
        ]

    def __str__(self):
        return f"Bid: {self.freelancer.username} → {self.project.title}"

    def save(self, *args, **kwargs):
        """Автоматически рассчитаем AI-оценку при создании"""
        if not self.pk:
            self.ai_score = self.project.ai_matching_score(self.freelancer)
        super().save(*args, **kwargs)


# ===== TRANSACTION MODELS =====

class Payment(models.Model):
    """Платёж/эскроу"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='payments')
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    
    # Провайдер платежа
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ('stripe', 'Stripe'),
            ('paypal', 'PayPal'),
            ('crypto', 'Cryptocurrency'),
        ],
        default='stripe'
    )
    transaction_id = models.CharField(max_length=200, unique=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Платёж'
        verbose_name_plural = 'Платежи'
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment: {self.amount} for {self.project.title}"


class Milestone(models.Model):
    """Этапы проекта"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='milestones')
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    deadline = models.DateTimeField()
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Ожидает'),
            ('in_progress', 'В работе'),
            ('completed', 'Завершено'),
            ('approved', 'Одобрено'),
            ('rejected', 'Отклонено'),
        ],
        default='pending'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Этап'
        verbose_name_plural = 'Этапы'
        ordering = ['deadline']

    def __str__(self):
        return f"{self.project.title} - {self.title}"


# ===== MESSAGE MODELS =====

class ProjectChat(models.Model):
    """Чат в проекте"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='chat')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat for {self.project.title}"


class ChatMessage(models.Model):
    """Сообщение в чате проекта"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    chat = models.ForeignKey(ProjectChat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    content = models.TextField()
    attachments = models.JSONField(default=list, blank=True)
    
    # Встраивание превью (Figma, Miro)
    embedded_url = models.URLField(blank=True, help_text='URL для встраивания (Figma, Miro)')
    embedded_type = models.CharField(
        max_length=20,
        choices=[
            ('figma', 'Figma'),
            ('miro', 'Miro'),
            ('other', 'Другое'),
        ],
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['chat', 'created_at']),
        ]

    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"


# ===== REVIEW MODELS =====

class Review(models.Model):
    """Отзыв после завершения проекта"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='given_reviews')
    reviewed_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_reviews')
    
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(max_length=1000)
    
    # Подробные оценки
    quality = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], help_text='Качество работы')
    communication = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], help_text='Коммуникация')
    deadline_adherence = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], help_text='Соблюдение сроков')
    professionalism = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], help_text='Профессионализм')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']
        unique_together = ['project', 'reviewer']

    def __str__(self):
        return f"Review: {self.reviewed_user.username} ({self.rating}/5)"


# ===== DISPUTE MODELS =====

class Dispute(models.Model):
    """Спор между участниками"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='disputes')
    
    initiator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='initiated_disputes')
    respondent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_disputes'
    )
    
    subject = models.CharField(max_length=200)
    description = models.TextField()
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('open', 'Открыт'),
            ('in_review', 'На рассмотрении'),
            ('resolved', 'Решен'),
            ('closed', 'Закрыт'),
        ],
        default='open'
    )
    
    resolution = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Спор'
        verbose_name_plural = 'Споры'
        ordering = ['-created_at']

    def __str__(self):
        return f"Dispute: {self.subject}"
