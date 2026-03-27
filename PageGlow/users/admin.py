from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserLevel, UserReputationLog


@admin.register(UserLevel)
class UserLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_reputation', 'icon', 'color', 'slug')
    list_display_links = ('name',)
    ordering = ('min_reputation',)
    search_fields = ('name', 'description')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'min_reputation', 'description')
        }),
        ('Внешний вид', {
            'fields': ('icon', 'color')
        }),
        ('Привилегии', {
            'fields': (
                'can_create_tags',
                'can_edit_own_posts_longer',
                'can_moderate_comments',
                'daily_upload_limit'
            )
        }),
        ('Автоматический бейдж', {
            'fields': ('auto_badge',),
            'description': 'Бейдж, который автоматически выдаётся при получении этого уровня'
        }),
    )


@admin.register(UserReputationLog)
class UserReputationLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'reason', 'created_at', 'get_related_object')
    list_display_links = ('user',)
    ordering = ('-created_at',)
    search_fields = ('user__username', 'reason')
    list_filter = ('reason', 'created_at')
    date_hierarchy = 'created_at'
    
    def get_related_object(self, obj):
        if obj.post:
            return f"Пост: {obj.post.title[:30]}"
        elif obj.comment:
            return "Комментарий"
        elif obj.discussion:
            return f"Обсуждение: {obj.discussion.title[:30]}"
        return "—"
    get_related_object.short_description = 'Связано с'


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('reputation', 'current_level')
    
    def reputation(self, obj):
        return obj.reputation
    reputation.short_description = 'Репутация'
    
    def current_level(self, obj):
        level = obj.current_level
        if level:
            return f"{level.icon} {level.name}"
        return "—"
    current_level.short_description = 'Уровень'
