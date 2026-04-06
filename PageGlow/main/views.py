
import logging
import os
import math
from bleach import clean
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q, Sum
from django.views.generic.edit import FormMixin, DeleteView
from requests import Response
from bs4 import BeautifulSoup, FeatureNotFound
from django.shortcuts import render
from rest_framework.mixins import UpdateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.generics import ListAPIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets, permissions
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.uploadedfile import UploadedFile
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, FormView, CreateView, UpdateView
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.core.cache import cache

from PageGlow import settings
from main import serializers
from main.serializers import PostSerializer
from .forms import AddPostForm, PostUpdateForm, UploadFileForm, CommentForm
from .models import (
    Post, Category, TagPost, UploadFiles, Comment, Subscription,
    Notification, Bookmark, Collection,
    UserBadge, UserAchievement
)
from .utils import DataMixin

logger = logging.getLogger(__name__)


def health_check(request):
    """Health check endpoint for Docker/Kubernetes"""
    try:
        from django.core.cache import cache
        cache.set('health_check', 'ok', 10)
        cache.get('health_check')
        return JsonResponse({'status': 'healthy', 'database': 'ok', 'cache': 'ok'})
    except Exception as e:
        logger.error(f'Health check failed: {str(e)}')
        return JsonResponse({'status': 'unhealthy', 'error': str(e)}, status=503)


def robots_txt(request):
    """Robots.txt endpoint"""
    return render(request, 'robots.txt', content_type='text/plain')


class AdminDashboardView(LoginRequiredMixin, DataMixin, TemplateView):
    """Dashboard для администраторов"""
    template_name = 'main/admin_dashboard.html'
    title_page = 'Панель администратора'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, 'Доступ запрещён')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        from django.db.models import Count, Sum, Q, Avg
        from django.utils import timezone
        from datetime import timedelta
        from django.contrib.auth import get_user_model
        from main.models import TagPost, Notification

        User = get_user_model()
        context = super().get_context_data(**kwargs)

        now = timezone.now()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Общая статистика
        context['total_posts'] = Post.objects.count()
        context['published_posts'] = Post.published.count()
        context['draft_posts'] = Post.objects.filter(is_published=False).count()
        context['total_users'] = User.objects.filter(is_active=True).count()
        context['active_users_count'] = User.objects.filter(
            is_active=True,
            last_login__gte=month_ago
        ).count()
        context['total_comments'] = Comment.objects.count()

        # Статистика за неделю
        context['posts_week'] = Post.objects.filter(
            time_create__gte=week_ago
        ).count()
        context['users_week'] = User.objects.filter(
            date_joined__gte=week_ago
        ).count()
        context['comments_week'] = Comment.objects.filter(
            created_at__gte=week_ago
        ).count()
        context['comments_today'] = Comment.objects.filter(
            created_at__gte=today
        ).count()

        # Статистика за месяц
        context['posts_month'] = Post.objects.filter(
            time_create__gte=month_ago
        ).count()
        context['users_month'] = User.objects.filter(
            date_joined__gte=month_ago
        ).count()

        # Просмотры и тренды
        total_views = Post.objects.aggregate(total=Sum('views'))['total'] or 0
        context['total_views'] = total_views
        
        views_this_week = Post.objects.filter(time_create__gte=week_ago).aggregate(
            total=Sum('views')
        )['total'] or 0
        views_last_week = Post.objects.filter(
            time_create__gte=week_ago - timedelta(days=7),
            time_create__lt=week_ago
        ).aggregate(total=Sum('views'))['total'] or 0
        context['views_trend'] = int(((views_this_week - max(views_last_week, 1)) / max(views_last_week, 1)) * 100) if views_last_week else 0

        # Процент опубликованных
        context['published_percentage'] = round((context['published_posts'] / max(context['total_posts'], 1)) * 100)

        # Средние значения
        context['avg_comments_per_post'] = Comment.objects.count() / max(Post.objects.count(), 1)
        context['avg_views_per_post'] = total_views / max(Post.objects.count(), 1)

        # Популярные статьи (топ 10)
        context['popular_posts'] = Post.published.select_related(
            'author', 'cat'
        ).annotate(
            likes_count=Count('likes')
        ).order_by('-views', '-likes_count')[:10]

        # Активные пользователи (топ 10 по постам)
        context['active_users'] = User.objects.annotate(
            posts_count=Count('posts', filter=Q(posts__is_published=True))
        ).filter(posts_count__gt=0).order_by('-posts_count')[:10]

        # Последние комментарии
        context['recent_comments'] = Comment.objects.select_related(
            'author', 'post'
        ).order_by('-created_at')[:10]

        # Статистика по категориям с цветами
        colors = ['#667eea', '#764ba2', '#11998e', '#38ef7d', '#00c6ff', '#0072ff', 
                  '#f093fb', '#f5576c', '#f6d365', '#fda085', '#ff9a9e', '#fecfef']
        category_stats = Category.objects.annotate(
            posts_count=Count('posts', filter=Q(posts__is_published=True))
        ).filter(posts_count__gt=0).order_by('-posts_count')
        
        # Добавляем цвета к категориям
        for i, cat in enumerate(category_stats):
            cat.color = colors[i % len(colors)]
        context['category_stats'] = category_stats

        # Теги
        context['tags_count'] = TagPost.objects.count()

        # Уведомления
        context['unread_notifications'] = Notification.objects.filter(
            is_read=False
        ).count()
        context['read_notifications'] = Notification.objects.filter(
            is_read=True
        ).count()

        # Статистика просмотров по дням (последние 30 дней)
        from django.db.models.functions import TruncDate

        daily_views = Post.objects.filter(
            time_create__gte=month_ago
        ).annotate(
            date=TruncDate('time_create')
        ).values('date').annotate(
            views=Sum('views'),
            posts=Count('id')
        ).order_by('date')

        # Конвертируем дату в строку для JSON
        context['daily_stats'] = [
            {'date': item['date'].strftime('%Y-%m-%d'), 'views': item['views'] or 0, 'posts': item['posts'] or 0}
            for item in daily_views
        ]

        return context


class AnalyticsAPIView(LoginRequiredMixin, View):
    """API для получения статистики"""
    def get(self, request):
        from django.db.models import Count, Sum, Q
        from django.utils import timezone
        from datetime import timedelta
        from django.http import JsonResponse
        from django.contrib.auth import get_user_model
        
        if not request.user.is_staff:
            return JsonResponse({'error': 'Доступ запрещён'}, status=403)
        
        User = get_user_model()
        now = timezone.now()
        period = request.GET.get('period', '30')  # дней
        
        try:
            period = int(period)
        except (ValueError, TypeError):
            period = 30
        
        start_date = now - timedelta(days=period)
        
        # Статистика
        stats = {
            'total_posts': Post.objects.count(),
            'published_posts': Post.published.count(),
            'total_users': User.objects.filter(is_active=True).count(),
            'total_comments': Comment.objects.count(),
            'period_stats': {
                'new_posts': Post.objects.filter(time_create__gte=start_date).count(),
                'new_users': User.objects.filter(date_joined__gte=start_date).count(),
                'new_comments': Comment.objects.filter(created_at__gte=start_date).count(),
            }
        }
        
        return JsonResponse(stats)


# ===== SOCIAL FEATURES =====

class BookmarksView(LoginRequiredMixin, DataMixin, ListView):
    """Закладки пользователя"""
    template_name = 'main/bookmarks.html'
    context_object_name = 'bookmarks'
    paginate_by = 15
    title_page = 'Мои закладки'

    def get_queryset(self):
        return Bookmark.objects.filter(
            user=self.request.user
        ).select_related('post', 'post__author', 'post__cat').annotate(
            post_likes_count=Count('post__likes', distinct=True)
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['collections'] = Collection.objects.filter(user=self.request.user)
        return context


class CollectionDetailView(LoginRequiredMixin, DataMixin, DetailView):
    """Детальный просмотр коллекции"""
    model = Collection
    template_name = 'main/collection_detail.html'
    context_object_name = 'collection'
    paginate_by = 15

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.user != request.user and not self.object.is_public:
            return redirect('bookmarks')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bookmarks_queryset = self.object.bookmarks.select_related(
            'post', 'post__author'
        ).order_by('-created_at')
        
        # Пагинация
        page_number = self.request.GET.get('page')
        paginator = Paginator(bookmarks_queryset, self.paginate_by)
        page_obj = paginator.get_page(page_number)
        
        context['bookmarks'] = page_obj
        context['page_obj'] = page_obj
        context['paginator'] = paginator
        return context


class BookmarkToggleView(LoginRequiredMixin, View):
    """Добавить/удалить закладку"""
    def post(self, request):
        post_id = request.POST.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        
        bookmark, created = Bookmark.objects.get_or_create(
            user=request.user,
            post=post
        )
        
        if not created:
            bookmark.delete()
            is_bookmarked = False
        else:
            is_bookmarked = True
            # Проверяем достижение "Коллекционер"
            bookmark_count = Bookmark.objects.filter(user=request.user).count()
            if bookmark_count == 10:
                badge, _ = UserBadge.objects.get_or_create(
                    key='collector',
                    defaults={
                        'name': 'Коллекционер',
                        'description': 'Собрано 10 закладок',
                        'icon': '📚',
                        'color': '#9c27b0'
                    }
                )
                UserAchievement.objects.get_or_create(
                    user=request.user,
                    badge=badge,
                    defaults={'reason': '10 закладок'}
                )
        
        return JsonResponse({
            'success': True,
            'is_bookmarked': is_bookmarked,
            'bookmarks_count': Bookmark.objects.filter(user=request.user).count()
        })


class CreateCollectionView(LoginRequiredMixin, CreateView):
    """Создание коллекции"""
    model = Collection
    fields = ['name', 'description', 'is_public']
    template_name = 'main/collection_form.html'
    success_url = reverse_lazy('bookmarks')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


def get_user_recommendations(request, limit=10):
    """
    Система рекомендаций статей для пользователя
    
    Алгоритм:
    1. Статьи из любимых категорий
    2. Статьи с похожими тегами
    3. Популярное за неделю
    """
    if not request.user.is_authenticated:
        return Post.published.order_by('-views', '-time_create')[:limit]
    
    # Любимые категории (где пользователь чаще всего читает)
    viewed_posts = Post.objects.filter(
        bookmarks__user=request.user
    ).values('cat').annotate(
        count=Count('id')
    ).order_by('-count')
    
    favorite_categories = [item['cat'] for item in viewed_posts[:5]]
    
    # Теги из закладок
    bookmarked_tags = Post.objects.filter(
        bookmarks__user=request.user
    ).values('tags').annotate(
        count=Count('id')
    ).order_by('-count')
    
    favorite_tags = [item['tags'] for item in bookmarked_tags[:10]]
    
    # Рекомендации
    recommendations = Post.published.exclude(
        bookmarks__user=request.user  # Исключаем уже сохранённые
    ).filter(
        Q(cat__in=favorite_categories) |
        Q(tags__in=favorite_tags)
    ).distinct().annotate(
        score=Count('likes') * 2 + Count('views') / 100
    ).order_by('-score', '-time_create')[:limit]
    
    if len(recommendations) < limit:
        # Дополняем популярным
        extra = Post.published.exclude(
            id__in=[p.id for p in recommendations]
        ).order_by('-views', '-time_create')[:limit - len(recommendations)]
        recommendations = list(recommendations) + list(extra)
    
    return recommendations


class MainHome(DataMixin, ListView):
    template_name = 'main/index.html'
    context_object_name = 'posts'
    title_page = 'Главная страница | ФлакХаб'
    cat_selected = 0
    paginate_by = 10

    def get_queryset(self):
        # Оптимизация: select_related для ForeignKey, prefetch_related для ManyToMany
        # annotate для Count чтобы избежать N+1 запросов
        return Post.published.select_related('cat', 'author').prefetch_related('tags').annotate(
            likes_count=Count('likes', distinct=True),
            favorites_count=Count('favorites', distinct=True)
        ).order_by('-time_create')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # SEO meta tags для главной страницы
        context.update({
            'meta_title': 'Платформа для IT-специалистов | ФлакХаб',
            'meta_description': 'Платформа для IT-специалистов: делитесь знаниями, находите возможности и развивайтесь вместе с нами. Публикация статей, руководств и новостей.',
            'meta_keywords': 'IT, программирование, разработка, технологии, статьи, руководство, Python, Django, веб-разработка',
            'meta_og_type': 'website',
        })
        return context

# class CustomSuccessMessageMixin:
#     @property
#     def success_msg(self):
#         return False
#
#     def form_valid(self, form):
#         messages.success(self.request, self.success_msg)
#         return super().form_valid(form)
#
#     def get_success_url(self):
#         return '%s?id=%s' % (self.success_url(), self.object.id)

class ShowPost(FormMixin, DataMixin, DetailView):
    template_name = 'main/post.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'
    form_class = CommentForm
    success_msg = 'Комментарий оставлен'

    def get_queryset(self):
        # Оптимизация: select_related для ForeignKey, prefetch_related для ManyToMany
        # annotate для Count чтобы избежать N+1 запросов
        return Post.published.select_related('author', 'cat').prefetch_related('tags').annotate(
            likes_count=Count('likes', distinct=True),
            favorites_count=Count('favorites', distinct=True),
            comments_count=Count('comments', distinct=True)
        )

    def get_success_url(self, **kwargs):
        return reverse_lazy('post', kwargs={'post_slug': self.get_object().slug})

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.post = self.get_object()
        self.object.author = self.request.user
        self.object.save()
        
        # Начисляем репутацию за создание комментария
        from users.reputation_utils import award_reputation
        award_reputation(
            user=self.object.author,
            reason='comment_created',
            comment=self.object
        )
        
        return super().form_valid(form)

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        post = get_object_or_404(queryset, slug=self.kwargs[self.slug_url_kwarg])

        # Увеличиваем счётчик просмотров
        session_key = f'viewed_post_{post.id}'
        if not self.request.session.get(session_key, False):
            post.views += 1
            post.save(update_fields=['views'])
            self.request.session[session_key] = True

        allowed_tags = [
            'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'ul', 'ol', 'li', 'strong', 'em', 'a', 'img',
            'blockquote', 'code', 'pre', 'i', 'span', 'u', 'br',
            'figure', 'figcaption', 'picture', 'source',
            'table', 'thead', 'tbody', 'tr', 'th', 'td',
        ]
        allowed_attributes = {
            '*': ['class', 'style'],
            'a': ['href', 'title', 'target', 'rel'],
            'img': ['src', 'alt', 'width', 'height', 'loading'],
            'figure': ['class'],
            'source': ['srcset', 'type', 'media'],
            'td': ['colspan', 'rowspan'],
            'th': ['colspan', 'rowspan'],
        }

        post.content = clean(post.content, tags=allowed_tags, attributes=allowed_attributes)
        return post

    def get_context_data(self, **kwargs):
        from django.core.paginator import Paginator
        from django.core.cache import cache

        context = super().get_context_data(**kwargs)
        post = self.object
        
        # Кэширование похожих постов
        cache_key = f'similar_posts_{post.id}'
        similar = cache.get(cache_key)
        if similar is None:
            similar = post.get_similar_posts()
            cache.set(cache_key, similar, 3600)  # 1 час
        context['similar_posts'] = similar
        
        # Кэширование времени чтения
        reading_cache_key = f'reading_time_{post.id}'
        reading_time = cache.get(reading_cache_key)
        if reading_time is None:
            reading_time = post.reading_time()
            cache.set(reading_cache_key, reading_time, 86400)  # 24 часа
        context['reading_time'] = reading_time

        # SEO meta tags для страницы поста
        context.update({
            'meta_title': f'{post.title} | PageGlow',
            'meta_description': post.get_meta_description(),
            'meta_keywords': ', '.join(post.get_keywords_list()),
            'meta_og_type': 'article',
            'meta_published_time': post.get_published_time(),
            'meta_modified_time': post.get_modified_time(),
            'meta_author': post.get_author_name(),
            'meta_section': post.get_category_name(),
            'meta_tags': post.get_tags_list(),
            'meta_image': post.get_image_full_url(),
        })

        # Оптимизация: prefetch_related для комментариев
        comments_qs = post.comments.select_related('author').prefetch_related('likes').order_by('-created_at')
        
        # Используем аннотированное значение comments_count для пагинации
        comments_count = getattr(post, 'comments_count', 0)
        
        # Создаем кастомный Paginator с закэшированным count
        class CachedPaginator(Paginator):
            @property
            def count(self):
                return comments_count
        
        comment_paginator = CachedPaginator(comments_qs, 20)  # 20 комментариев на страницу
        
        page_number = self.request.GET.get('comments-page')
        context['comments_page'] = comment_paginator.get_page(page_number)
        context['comments_count'] = comments_count

        # Проверяем подписку на автора
        if self.request.user.is_authenticated and post.author:
            context['is_subscribed'] = Subscription.objects.filter(
                subscriber=self.request.user,
                author=post.author
            ).exists()
        return context


@login_required
def about(request):
    context = {
        'default_image': settings.DEFAULT_USER_IMAGE,
    }
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            fp = UploadFiles(file=form.cleaned_data['file'])
            fp.save()
    else:
        form = UploadFileForm()
    return render(request, 'main/about.html', {'title' : 'О сайте', 'form': form, 'context': context})

def contact(request):
    return render(request, 'main/contact.html')

class AddPage(LoginRequiredMixin, DataMixin, CreateView):
    form_class = AddPostForm
    template_name = 'main/addpage.html'
    title_page = 'Добавление статьи'

    def form_valid(self, form):
        html_content = form.cleaned_data['content']
        soup = BeautifulSoup(html_content, 'html.parser')
        heading = soup.find(['h1', 'h2', 'h3'])

        w = form.save(commit=False)
        w.author = self.request.user

        if heading:
            form.instance.title = heading.get_text(strip=True)
            heading.decompose()
            form.instance.content = str(soup)
        else:
            form.instance.title = 'Без заголовка'

        # Сохраняем пост
        response = super().form_valid(form)

        # Начисляем репутацию за создание поста
        post = self.object
        if post.author:
            from users.reputation_utils import award_reputation
            award_reputation(
                user=post.author,
                reason='post_created',
                post=post
            )

        # Очищаем кэш сайдбара
        cache.clear()

        # Создаём уведомления для подписчиков
        if post.author:
            # Получаем всех подписчиков автора
            subscribers = Subscription.objects.filter(author=post.author).select_related('subscriber')
            for sub in subscribers:
                if sub.subscriber != post.author:  # Не уведомлять самого автора
                    notification = Notification.objects.create(
                        recipient=sub.subscriber,
                        sender=post.author,
                        notification_type='new_post',
                        post=post,
                        message=f'{post.author.username} опубликовал новую статью "{post.title[:30]}..."'
                    )
                    # Отправляем уведомление через WebSocket
                    try:
                        from main.consumers import send_notification_to_user
                        send_notification_to_user(sub.subscriber.id, {
                            'id': notification.id,
                            'message': notification.message,
                            'type': notification.notification_type,
                            'post_url': post.get_absolute_url(),
                            'created_at': notification.created_at.isoformat()
                        })
                    except Exception as e:
                        logger.error(f'Ошибка отправки WebSocket уведомления: {e}')

        return response

    def get_success_url(self):
            return reverse_lazy('users:profile')
    


class UpdatePage(LoginRequiredMixin, DataMixin, UpdateView):
    model = Post
    form_class = AddPostForm  # Используем AddPostForm вместо PostUpdateForm
    template_name = 'main/addpage.html'
    title_page = 'Редактирование статьи'

    def get_queryset(self):
        # Пользователь может редактировать только свои статьи
        return Post.objects.filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title_page
        return context

    def form_valid(self, form):
        # Получаем HTML контент из формы
        html_content = form.cleaned_data['content']
        
        # Сохраняем текущий заголовок (на случай если не найдём новый)
        current_title = self.object.title
        
        # Пытаемся извлечь заголовок из контента если он есть
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            heading = soup.find(['h1', 'h2', 'h3'])

            if heading:
                heading_text = heading.get_text(strip=True)
                # Проверяем на стандартные placeholder'ы
                placeholder_list = [
                    'заголовок', 'заголовок статьи', 'title', 'heading',
                    'заголовок...', 'ваш заголовок', 'введите заголовок'
                ]
                
                if heading_text.lower() not in placeholder_list:
                    form.instance.title = heading_text
                    heading.decompose()
                    form.instance.content = str(soup)
                else:
                    # Если placeholder - оставляем существующий title
                    form.instance.title = current_title
                    heading.decompose()
                    form.instance.content = str(soup)
            else:
                # Если заголовка нет в контенте - оставляем старый
                form.instance.title = current_title
        except Exception as e:
            logger.error(f'Ошибка обработки контента: {e}')
            form.instance.title = current_title

        # Сохраняем объект
        self.object = form.save()

        # Очищаем кэш сайдбара
        cache.clear()

        # Выводим сообщение об успехе
        from django.contrib import messages
        messages.success(self.request, 'Статья успешно обновлена!')
        
        # Перенаправляем на страницу статьи
        return redirect('post', post_slug=self.object.slug)

    def form_invalid(self, form):
        # Выводим сообщение об ошибке
        from django.contrib import messages
        messages.error(self.request, f'Ошибка сохранения: {form.errors}')
        return super().form_invalid(form)

def login(request):
    return render(request, 'main/login.html')

class PostDeleteView(LoginRequiredMixin, DataMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('users:profile')

    def form_valid(self, form):
        print(f"Удален объект: {self.object}")
        
        # Очищаем кэш сайдбара
        cache.clear()
        
        return super().form_valid(form)

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

class MainCategory(DataMixin, ListView):
    template_name = 'main/index.html'
    context_object_name = 'posts'
    allow_empty = False
    paginate_by = 10

    def get_queryset(self):
        # Оптимизация: select_related для cat, prefetch_related для tags и author
        # annotate для Count чтобы избежать N+1 запросов
        return Post.published.select_related('cat', 'author').prefetch_related('tags').annotate(
            likes_count=Count('likes', distinct=True),
            favorites_count=Count('favorites', distinct=True)
        ).filter(
            cat__slug=self.kwargs['cat_slug']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cat = context["posts"][0].cat
        return self.get_mixin_context(context, title='Категория - ' + cat.name, cat_selected=cat.pk)

def page_not_found(request, exception):
    return render(request, '404.html', status=404)

def server_error(request):
    return render(request, '500.html', status=500)

def bad_gateway(request):
    return render(request, '502.html', status=502)

def service_unavailable(request):
    return render(request, '503.html', status=503)

def permission_denied(request, exception):
    return render(request, '403.html', status=403)

class TagPostList(DataMixin, ListView):
    template_name = 'main/index.html'
    context_object_name = 'posts'
    allow_empty = False
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = TagPost.objects.get(slug=self.kwargs['tag_slug'])
        return self.get_mixin_context(context, title='Тег: ' + tag.tag)

    def get_queryset(self):
        # Оптимизация: select_related для cat и author, prefetch_related для tags
        # annotate для Count чтобы избежать N+1 запросов
        return Post.published.select_related('cat', 'author').prefetch_related('tags').annotate(
            likes_count=Count('likes', distinct=True),
            favorites_count=Count('favorites', distinct=True)
        ).filter(
            tags__slug=self.kwargs['tag_slug']
        )


class Search(DataMixin, ListView):
    template_name = 'main/search.html'
    context_object_name = 'posts'
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        post_type = self.request.GET.get('type', 'all')
        sort = self.request.GET.get('sort', 'relevance')

        if query:
            search = Post.published.select_related('cat', 'author').prefetch_related('tags').annotate(
                likes_count=Count('likes', distinct=True),
                favorites_count=Count('favorites', distinct=True)
            )

            # Фильтр по типу контента
            if post_type == 'articles':
                search = search.filter(post_type=Post.PostType.ARTICLE)
            elif post_type == 'posts':
                search = search.filter(post_type=Post.PostType.POST)
            elif post_type == 'news':
                search = search.filter(post_type=Post.PostType.NEWS)
            elif post_type == 'ideas':
                search = search.filter(post_type=Post.PostType.IDEA)

            # Поиск по title и content
            search = search.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            )

            # Сортировка
            if sort == 'date':
                search = search.order_by('-time_create')
            elif sort == 'views':
                search = search.order_by('-views')
        else:
            search = Post.published.select_related('cat', 'author').prefetch_related('tags').annotate(
                likes_count=Count('likes', distinct=True),
                favorites_count=Count('favorites', distinct=True)
            ).order_by('-time_create')

        return search

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request
        context['q'] = request.GET.get('q', '')
        context['post_type'] = request.GET.get('type', 'all')
        context['sort'] = request.GET.get('sort', 'relevance')
        context['categories'] = Category.objects.all()
        context['title'] = 'Поиск'
        return context


@method_decorator(login_required, name='dispatch')
class PostLikeAjaxView(View):
    def post(self, request, *args, **kwargs):
        post_id = request.POST.get('post_id')
        post = get_object_or_404(Post, id=post_id)

        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
            liked = False
            # Отменяем репутацию при удалении лайка
            if post.author and post.author != request.user:
                from users.reputation_utils import undo_reputation
                undo_reputation(
                    user=post.author,
                    reason='post_liked',
                    post=post
                )
        else:
            post.likes.add(request.user)
            liked = True
            # Начисляем репутацию автору за лайк
            if post.author and post.author != request.user:
                from users.reputation_utils import award_reputation
                award_reputation(
                    user=post.author,
                    reason='post_liked',
                    post=post
                )
            
            # Уведомление автору о лайке
            if post.author and post.author != request.user:
                notification = Notification.objects.create(
                    recipient=post.author,
                    sender=request.user,
                    notification_type='like',
                    post=post,
                    message=f'{request.user.username} оценил вашу статью "{post.title[:30]}..."'
                )
                # Отправляем уведомление через WebSocket
                try:
                    from main.consumers import send_notification_to_user
                    send_notification_to_user(post.author.id, {
                        'id': notification.id,
                        'message': notification.message,
                        'type': notification.notification_type,
                        'post_url': post.get_absolute_url(),
                        'created_at': notification.created_at.isoformat()
                    })
                except Exception as e:
                    logger.error(f'Ошибка отправки WebSocket уведомления: {e}')

        data = {
            'success': True,
            'liked': liked,
            'likes_count': post.number_of_likes()
        }
        return JsonResponse(data)

@method_decorator(login_required, name='dispatch')
class PostFavoriteAjaxView(View):
    def post(self, request, *args, **kwargs):
        post_id = request.POST.get('post_id')
        post = get_object_or_404(Post, id=post_id)

        if post.favorites.filter(id=request.user.id).exists():
            # Убираем из избранного
            post.favorites.remove(request.user)
            favorited = False
        else:
            # Добавляем в избранное
            post.favorites.add(request.user)
            favorited = True

        data = {
            'success': True,
            'favorited': favorited,
            'favorites_count': post.number_of_favorites()
        }
        return JsonResponse(data)
    
@method_decorator(login_required, name='dispatch')
class AddCommentAjaxView(View):
    def post(self, request, *args, **kwargs):
        try:
            post_id = request.POST.get('post_id')
            content = request.POST.get('content')
            parent_id = request.POST.get('parent_id')

            if not content or len(content.strip()) == 0:
                return JsonResponse({
                    'success': False,
                    'error': 'Текст комментария не может быть пустым'
                }, status=400)

            post = get_object_or_404(Post, id=post_id)
            
            parent = None
            if parent_id:
                parent = get_object_or_404(Comment, id=parent_id)

            comment = Comment.objects.create(
                post=post,
                author=request.user,
                content=content,
                parent=parent
            )

            # Уведомление автору статьи о комментарии
            if post.author and post.author != request.user:
                notification = Notification.objects.create(
                    recipient=post.author,
                    sender=request.user,
                    notification_type='comment',
                    post=post,
                    comment=comment,
                    message=f'{request.user.username} прокомментировал "{post.title[:30]}..."'
                )
                try:
                    from main.consumers import send_notification_to_user
                    send_notification_to_user(post.author.id, {
                        'id': notification.id,
                        'message': notification.message,
                        'type': notification.notification_type,
                        'post_url': post.get_absolute_url(),
                        'created_at': notification.created_at.isoformat()
                    })
                except Exception as e:
                    logger.error(f'Ошибка отправки WebSocket уведомления: {e}')

            # Уведомление автору родительского комментария (если это ответ)
            if parent and parent.author != request.user:
                notification = Notification.objects.create(
                    recipient=parent.author,
                    sender=request.user,
                    notification_type='comment',
                    post=post,
                    comment=comment,
                    message=f'{request.user.username} ответил на ваш комментарий'
                )

            data = {
                'success': True,
                'comment': {
                    'id': comment.id,
                    'content': comment.content,
                    'author': comment.author.username,
                    'created_at': comment.created_at.strftime('%d.%m.%Y %H:%M'),
                    'is_active': comment.is_active,
                    'parent_id': parent.id if parent else None,
                    'parent_author': parent.author.username if parent else None,
                    'likes_count': 0,
                    'is_liked': False,
                    'can_delete': True,
                    'replies_count': 0
                }
            }
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

@method_decorator(login_required, name='dispatch')
class DeleteCommentAjaxView(View):
    def post(self, request, *args, **kwargs):
        try:
            comment_id = request.POST.get('comment_id')
            if not comment_id:
                return JsonResponse({'success': False, 'error': 'ID комментария не указан'}, status=400)

            comment = get_object_or_404(Comment, id=comment_id)

            # Проверяем, что пользователь — автор комментария или администратор
            if comment.author != request.user and not request.user.is_staff:
                return JsonResponse(
                    {'success': False, 'error': 'У вас нет прав для удаления этого комментария'},
            status=403
        )

            comment.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

@method_decorator(login_required, name='dispatch')
class ToggleCommentLikeAjaxView(View):
    def post(self, request, *args, **kwargs):
        try:
            comment_id = request.POST.get('comment_id')
            if not comment_id:
                return JsonResponse({'success': False, 'error': 'ID комментария не указан'}, status=400)

            comment = get_object_or_404(Comment, id=comment_id)

            # Переключаем лайк
            if comment.likes.filter(id=request.user.id).exists():
                comment.likes.remove(request.user)
                is_liked = False
                # Отменяем репутацию при удалении лайка
                if comment.author != request.user:
                    from users.reputation_utils import undo_reputation
                    undo_reputation(
                        user=comment.author,
                        reason='comment_liked',
                        comment=comment
                    )
            else:
                comment.likes.add(request.user)
                is_liked = True
                # Начисляем репутацию автору за лайк
                if comment.author != request.user:
                    from users.reputation_utils import award_reputation
                    award_reputation(
                        user=comment.author,
                        reason='comment_liked',
                        comment=comment
                    )

                # Уведомление автору комментария о лайке
                if comment.author != request.user:
                    Notification.objects.create(
                        recipient=comment.author,
                        sender=request.user,
                        notification_type='like',
                        post=comment.post,
                        comment=comment,
                        message=f'{request.user.username} лайкнул ваш комментарий'
                    )

            data = {
                'success': True,
                'is_liked': is_liked,
                'likes_count': comment.number_of_likes()
            }
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
        


# @login_required
# def toggle_favorite(request, post_id):
#     post = get_object_or_404(Post, id=post_id, author=request.user)
#     post.is_favorite = not post.is_favorite
#     post.save()
#     return redirect('profile')

@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class CKEditorUploadView(View):
    """Upload view для CKEditor 5 - совместим с django_ckeditor_5"""
    def post(self, request):
        try:
            # django_ckeditor_5 отправляет файл в поле 'upload'
            file = request.FILES.get('upload')
            
            # Если нет файла, пробуем 'file'
            if not file:
                file = request.FILES.get('file')
            
            logger.info(f"Upload request: file={file}, content_type={file.content_type if file else None}")
            
            if not file:
                logger.warning("No file in request.FILES")
                return JsonResponse({
                    'error': {
                        'message': 'Файл не найден'
                    }
                }, status=400)

            if file.size > 100 * 1024 * 1024:
                logger.warning(f"File too large: {file.size}")
                return JsonResponse({
                    'error': {
                        'message': 'Файл слишком большой (макс. 100 МБ)'
                    }
                }, status=400)

            # Разрешённые типы файлов
            allowed_types = [
                'image/jpeg',
                'image/png',
                'image/gif',
                'image/webp',
                'image/x-icon',
                'image/vnd.microsoft.icon',
                'image/svg+xml'
            ]
            if file.content_type not in allowed_types:
                logger.warning(f"Invalid file type: {file.content_type}")
                return JsonResponse({
                    'error': {
                        'message': f'Недопустимый тип файла: {file.content_type}. Разрешены: JPEG, PNG, GIF, WebP, ICO, SVG'
                    }
                }, status=400)

            # Создаём директорию для загрузок
            upload_path = os.path.join(settings.MEDIA_ROOT, 'ckeditor', 'uploads')
            os.makedirs(upload_path, exist_ok=True)
            logger.info(f"Upload path: {upload_path}")

            # Генерируем уникальное имя файла
            import uuid
            ext = file.name.split('.')[-1] if '.' in file.name else 'jpg'
            unique_filename = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex
            logger.info(f"Saving file as: {unique_filename}")

            fs = FileSystemStorage(location=upload_path)
            fs.save(unique_filename, file)
            logger.info(f"File saved successfully")

            # Формируем правильный URL
            file_url = f"{settings.MEDIA_URL}ckeditor/uploads/{unique_filename}"
            logger.info(f"File URL: {file_url}")

            # django_ckeditor_5 ожидает такой формат ответа
            return JsonResponse({
                'url': file_url,
                'uploaded': True,
            })
        except Exception as e:
            logger.error(f"Upload error: {str(e)}", exc_info=True)
            return JsonResponse({
                'error': {
                    'message': f'Ошибка загрузки: {str(e)}'
                }
            }, status=500)


class PopularPostsView(DataMixin, ListView):
    """Популярные статьи"""
    template_name = 'main/index.html'
    context_object_name = 'posts'
    title_page = 'Популярное'
    paginate_by = 10

    def get_queryset(self):
        return Post.published.annotate(
            likes_count=Count('likes', distinct=True),
            favorites_count=Count('favorites', distinct=True)
        ).all().order_by('-views')


@method_decorator(login_required, name='dispatch')
class SubscribeAuthorView(View):
    """Подписка/отписка от автора"""
    def post(self, request, *args, **kwargs):
        from users.models import User
        author_id = request.POST.get('author_id')
        author = get_object_or_404(User, id=author_id, is_active=True)

        if author == request.user:
            return JsonResponse({'success': False, 'error': 'Нельзя подписаться на себя'}, status=400)

        subscription, created = Subscription.objects.get_or_create(
            subscriber=request.user,
            author=author
        )

        if not created:
            subscription.delete()
            subscribed = False
        else:
            subscribed = True
            # Начисляем репутацию автору за подписку
            from users.reputation_utils import award_reputation
            award_reputation(
                user=author,
                reason='subscription_received',
                skip_limit=True
            )
            
            # Создаём уведомление для автора
            notification = Notification.objects.create(
                recipient=author,
                sender=request.user,
                notification_type='follow',
                message=f'{request.user.username} подписался на вас'
            )
            # Отправляем уведомление через WebSocket
            try:
                from main.consumers import send_notification_to_user
                send_notification_to_user(author.id, {
                    'id': notification.id,
                    'message': notification.message,
                    'type': notification.notification_type,
                    'created_at': notification.created_at.isoformat()
                })
            except Exception as e:
                logger.error(f'Ошибка отправки WebSocket уведомления: {e}')

        subscribers_count = Subscription.objects.filter(author=author).count()

        return JsonResponse({
            'success': True,
            'subscribed': subscribed,
            'subscribers_count': subscribers_count
        })


class SubscriptionFeedView(LoginRequiredMixin, DataMixin, ListView):
    """Лента подписок"""
    template_name = 'main/index.html'
    context_object_name = 'posts'
    title_page = 'Мои подписки'
    paginate_by = 10

    def get_queryset(self):
        subscribed_authors = Subscription.objects.filter(
            subscriber=self.request.user
        ).values_list('author_id', flat=True)
        return Post.published.filter(author_id__in=subscribed_authors).annotate(
            likes_count=Count('likes', distinct=True),
            favorites_count=Count('favorites', distinct=True)
        ).order_by('-time_create')


@method_decorator(login_required, name='dispatch')
class NotificationsView(View):
    """Получение уведомлений"""
    def get(self, request, *args, **kwargs):
        try:
            base_qs = Notification.objects.filter(
                recipient=request.user
            ).select_related('sender', 'post', 'comment').order_by('-created_at')

            # Сначала считаем непрочитанные (до слайса)
            unread_count = base_qs.filter(is_read=False).count()

            # Затем применяем слайс
            notifications = base_qs[:20]

            data = {
                'unread_count': unread_count,
                'notifications': [
                    {
                        'id': n.id,
                        'type': n.notification_type,
                        'message': n.message,
                        'is_read': n.is_read,
                        'created_at': n.created_at.strftime('%d.%m.%Y %H:%M'),
                        'post_url': n.post.get_absolute_url() if n.post else None,
                        'sender_username': n.sender.username if n.sender else None,
                    }
                    for n in notifications
                ]
            }
            return JsonResponse(data)
        except Exception as e:
            logger.error(f"Notifications error: {str(e)}", exc_info=True)
            return JsonResponse({
                'error': str(e)
            }, status=500)


@method_decorator(login_required, name='dispatch')
class MarkNotificationsReadView(View):
    """Пометить уведомления как прочитанные"""
    def post(self, request, *args, **kwargs):
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'success': True})


# ===== ДОПОЛНИТЕЛЬНЫЕ СТРАНИЦЫ =====

def about_us(request):
    """О нас"""
    context = {
        'title': 'О платформе ФлакХаб',
    }
    return render(request, 'main/about_us.html', context)


def terms_of_use(request):
    """Условия использования"""
    context = {
        'title': 'Условия использования',
    }
    return render(request, 'main/terms_of_use.html', context)


def privacy_policy(request):
    """Политика конфиденциальности"""
    context = {
        'title': 'Политика конфиденциальности',
    }
    return render(request, 'main/privacy_policy.html', context)