from django.contrib import admin, messages
from django.utils.safestring import mark_safe


from .models import Post, Category, TagPost, Discussion, DiscussionComment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    fields = ['title', 'content', 'photo','post_photo','is_published', 'cat', 'tags']
    list_display = ('title', 'post_photo' ,'time_create','is_published', 'cat')
    readonly_fields = ['post_photo']
    list_display_links = ('title',)
    filter_horizontal = ('tags',)
    ordering = ['time_create', 'title']
    list_editable = ('is_published',)
    list_per_page = 10
    actions = ['set_published', 'set_draft']
    search_fields = ['title', 'cat__name']
    list_filter = ('cat__name', 'is_published')
    save_on_top = True

    @admin.display(description='Изображение', ordering='content')
    def post_photo(self, main:Post):
        if main.photo:
            return mark_safe(f'<img src="{main.photo.url}" width="50">')
        return 'Без фото'


    @admin.action(description='Опубликовать выбранные записи')
    def set_published(self, request, queryset):
        count = queryset.update(is_published=Post.Status.PUBLISHED)
        self.message_user(request, f'Опубликовано {count} записей', messages.SUCCESS)


    @admin.action(description='Снять с публикации выбранные записи')
    def set_draft(self, request, queryset):
        count = queryset.update(is_published=Post.Status.DRAFT)
        self.message_user(request, f'{count} записей сняты с публикации!', messages.WARNING)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    readonly_fields = ['slug']
    list_display_links = ('id', 'name')
# admin.site.register(Post, PostAdmin)

@admin.register(TagPost)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('id', 'tag')
    readonly_fields = ['slug']
    list_display_links = ('id', 'tag')


@admin.register(Discussion)
class DiscussionAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'cat', 'views', 'is_published', 'is_closed', 'time_create')
    list_filter = ('is_published', 'is_closed', 'cat', 'time_create')
    search_fields = ('title', 'content', 'author__username')
    readonly_fields = ('time_create', 'time_update', 'views')
    list_editable = ('is_published', 'is_closed')
    ordering = ('-time_create',)
    list_per_page = 20
    save_on_top = True
    filter_horizontal = ('tags',)


@admin.register(DiscussionComment)
class DiscussionCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'discussion', 'author', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('content', 'author__username', 'discussion__title')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    list_per_page = 20
    save_on_top = True
