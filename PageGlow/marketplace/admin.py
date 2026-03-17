from django.contrib import admin
from django.utils.html import format_html
from . import models


@admin.register(models.Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'category']
    list_filter = ['category']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(models.FreelancerProfile)
class FreelancerProfileAdmin(admin.ModelAdmin):
    list_display = ['get_username', 'role', 'rating', 'total_projects', 'is_verified', 'is_available']
    list_filter = ['role', 'is_verified', 'is_available', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['rating', 'total_reviews', 'total_projects', 'total_earned', 'created_at', 'updated_at']
    filter_horizontal = ['skills']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'role', 'bio', 'avatar')
        }),
        ('Опыт и навыки', {
            'fields': ('years_experience', 'skills')
        }),
        ('Портфолио', {
            'fields': ('portfolio_url', 'github_url', 'linkedin_url')
        }),
        ('Статистика', {
            'fields': ('rating', 'total_reviews', 'total_projects', 'total_earned'),
            'classes': ('collapse',)
        }),
        ('Статус и цены', {
            'fields': ('is_verified', 'is_available', 'hourly_rate')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Пользователь'


@admin.register(models.CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'get_contact_email', 'rating', 'total_projects', 'total_spent']
    list_filter = ['rating', 'created_at']
    search_fields = ['company_name', 'user__email']
    readonly_fields = ['rating', 'total_reviews', 'total_projects', 'total_spent', 'created_at', 'updated_at']
    
    def get_contact_email(self, obj):
        return obj.user.email
    get_contact_email.short_description = 'Email'


class MilestoneInline(admin.TabularInline):
    model = models.Milestone
    extra = 0


class BidInline(admin.TabularInline):
    model = models.Bid
    extra = 0
    readonly_fields = ['freelancer', 'ai_score', 'proposed_price', 'estimated_days', 'created_at']
    can_delete = False


@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'get_client', 'status', 'budget_max', 'deadline', 'get_assigned']
    list_filter = ['status', 'category', 'difficulty', 'is_urgent', 'created_at']
    search_fields = ['title', 'description', 'client__username']
    readonly_fields = ['id', 'created_at', 'updated_at', 'budget_remaining']
    filter_horizontal = ['required_skills']
    inlines = [MilestoneInline, BidInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('id', 'title', 'description', 'client')
        }),
        ('Требования', {
            'fields': ('required_skills', 'category', 'difficulty')
        }),
        ('Бюджет и сроки', {
            'fields': ('budget_min', 'budget_max', 'budget_type', 'currency', 'deadline', 'budget_remaining')
        }),
        ('Статус', {
            'fields': ('status', 'assigned_to', 'is_urgent')
        }),
        ('Вложения', {
            'fields': ('attachments',),
            'classes': ('collapse',)
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_client(self, obj):
        return obj.client.username
    get_client.short_description = 'Заказчик'
    
    def get_assigned(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.username
        return '-'
    get_assigned.short_description = 'Назначен'


@admin.register(models.Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ['get_freelancer', 'get_project', 'proposed_price', 'ai_score', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['freelancer__username', 'project__title']
    readonly_fields = ['id', 'ai_score', 'created_at', 'updated_at']
    
    def get_freelancer(self, obj):
        return obj.freelancer.username
    get_freelancer.short_description = 'Фрилансер'
    
    def get_project(self, obj):
        return obj.project.title
    get_project.short_description = 'Проект'


@admin.register(models.Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ['title', 'get_project', 'amount', 'deadline', 'status']
    list_filter = ['status', 'deadline']
    search_fields = ['title', 'project__title']
    
    def get_project(self, obj):
        return obj.project.title
    get_project.short_description = 'Проект'


@admin.register(models.Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_project', 'amount', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['project__title', 'transaction_id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def get_project(self, obj):
        return obj.project.title
    get_project.short_description = 'Проект'


class ChatMessageInline(admin.TabularInline):
    model = models.ChatMessage
    extra = 0
    readonly_fields = ['sender', 'content', 'created_at']
    can_delete = False


@admin.register(models.ProjectChat)
class ProjectChatAdmin(admin.ModelAdmin):
    list_display = ['get_project', 'get_message_count', 'created_at']
    search_fields = ['project__title']
    inlines = [ChatMessageInline]
    
    def get_project(self, obj):
        return obj.project.title
    get_project.short_description = 'Проект'
    
    def get_message_count(self, obj):
        return obj.messages.count()
    get_message_count.short_description = 'Сообщений'


@admin.register(models.ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['get_sender', 'get_chat', 'get_content_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['sender__username', 'content']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def get_sender(self, obj):
        return obj.sender.username
    get_sender.short_description = 'Отправитель'
    
    def get_chat(self, obj):
        return obj.chat.project.title
    get_chat.short_description = 'Проект'
    
    def get_content_preview(self, obj):
        return obj.content[:50]
    get_content_preview.short_description = 'Содержание'


@admin.register(models.Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['get_reviewer', 'get_reviewed', 'rating', 'quality', 'communication', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['reviewer__username', 'reviewed_user__username']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def get_reviewer(self, obj):
        return obj.reviewer.username
    get_reviewer.short_description = 'Рецензент'
    
    def get_reviewed(self, obj):
        return obj.reviewed_user.username
    get_reviewed.short_description = 'Оцененный пользователь'
@admin.register(models.Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ['subject', 'get_initiator', 'get_respondent', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['subject', 'initiator__username', 'respondent__username']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def get_initiator(self, obj):
        return obj.initiator.username
    get_initiator.short_description = 'Инициатор'
    
    def get_respondent(self, obj):
        return obj.respondent.username
    get_respondent.short_description = 'Ответчик'
