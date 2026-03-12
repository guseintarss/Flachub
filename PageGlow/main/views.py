
import logging
import os
from bleach import clean
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
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
import math
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
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

from PageGlow import settings
from main import serializers
from main.serializers import PostSerializer
from .forms import AddPostForm, AddQuestionForm, PostUpdateForm, UploadFileForm, CommentForm
from .models import Post, Category, TagPost, UploadFiles, Comment, Subscription, Notification
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



class MainHome(DataMixin, ListView):
    template_name = 'main/index.html'
    context_object_name = 'posts'
    title_page = 'Главная страница | PageGlow'
    cat_selected = 0


    def get_queryset(self):
        return Post.published.all().select_related('cat', 'author')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
        return super().form_valid(form)

    def get_object(self, queryset=None):
        post = get_object_or_404(Post.published, slug=self.kwargs[self.slug_url_kwarg])
        
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
        context = super().get_context_data(**kwargs)
        post = self.object
        context['similar_posts'] = post.get_similar_posts()
        context['reading_time'] = post.reading_time()
        
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

        return super().form_valid(form)
    
    def get_success_url(self):
            return reverse_lazy('users:profile')
    


class UpdatePage(LoginRequiredMixin, DataMixin, UpdateView):
    model = Post
    form_class = PostUpdateForm
    template_name = 'main/addpage.html'
    success_url = reverse_lazy('home')
    title_page = 'Редактирование статьи'
    

    def get_success_url(self, **kwargs):
        return reverse_lazy('post', kwargs={'post_slug': self.get_object().slug})

def login(request):
    return render(request, 'main/login.html')

class PostDeleteView(LoginRequiredMixin, DataMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('users:profile')

    def form_valid(self, form):
        print(f"Удален объект: {self.object}")
        return super().form_valid(form)

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

class MainCategory(DataMixin, ListView):
    template_name = 'main/index.html'
    context_object_name = 'posts'
    allow_empty = False

    def get_queryset(self):
        return Post.published.filter(cat__slug=self.kwargs['cat_slug']).select_related('cat')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cat = context["posts"][0].cat
        return self.get_mixin_context(context, title='Категория - ' + cat.name, cat_selected=cat.pk)

def page_not_found(request, exception):
    return render(request, '404.html', status=404)

class TagPostList(DataMixin, ListView):
    template_name = 'main/index.html'
    context_object_name = 'posts'
    allow_empty = False

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = TagPost.objects.get(slug=self.kwargs['tag_slug'])
        return self.get_mixin_context(context, title='Тег: ' + tag.tag)

    def get_queryset(self):
        return Post.published.filter(tags__slug=self.kwargs['tag_slug']).select_related('cat')


class Search(DataMixin, ListView):
    template_name = 'main/index.html'
    context_object_name = 'posts'

    def get_queryset(self):
        query = self.request.GET.get('q', '')  # Получаем поисковый запрос (пустая строка, если нет)

        if query:
            # Ищем совпадение в title ИЛИ в content (без учёта регистра)
            search = Post.published.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query)
            )
        else:
            # Если запроса нет — возвращаем все опубликованные посты
            search = Post.published.all()

        return search


    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['q'] = self.request.GET.get('q')
        return context


@method_decorator(login_required, name='dispatch')
class PostLikeAjaxView(View):
    def post(self, request, *args, **kwargs):
        post_id = request.POST.get('post_id')
        post = get_object_or_404(Post, id=post_id)

        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True
            # Уведомление автору о лайке
            if post.author and post.author != request.user:
                Notification.objects.create(
                    recipient=post.author,
                    sender=request.user,
                    notification_type='like',
                    post=post,
                    message=f'{request.user.username} оценил вашу статью "{post.title[:30]}..."'
                )

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

            if not content or len(content.strip()) == 0:
                return JsonResponse({
                    'success': False,
                    'error': 'Текст комментария не может быть пустым'
                }, status=400)

            post = get_object_or_404(Post, id=post_id)

            comment = Comment.objects.create(
                post=post,
                author=request.user,
                content=content
            )
            
            # Уведомление автору статьи о комментарии
            if post.author and post.author != request.user:
                Notification.objects.create(
                    recipient=post.author,
                    sender=request.user,
                    notification_type='comment',
                    post=post,
                    comment=comment,
                    message=f'{request.user.username} прокомментировал "{post.title[:30]}..."'
                )

            data = {
                'success': True,
                'comment': {
                    'id': comment.id,
                    'content': comment.content,
                    'author': comment.author.username,
                    'created_at': comment.created_at.strftime('%d.%m.%Y %H:%M'),
                    'is_active': comment.is_active
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
        


# @login_required
# def toggle_favorite(request, post_id):
#     post = get_object_or_404(Post, id=post_id, author=request.user)
#     post.is_favorite = not post.is_favorite
#     post.save()
#     return redirect('profile')

@method_decorator(login_required, name='dispatch')
class CKEditorUploadView(View):
    def post(self, request):
        file = request.FILES.get('upload')
        if not file:
            return JsonResponse({
                'error': {'message': 'Файл не найден'}
            }, status=400)

        if file.size > 100 * 1024 * 1024:
            return JsonResponse({
                'error': {'message': 'Файл слишком большой (макс. 100 МБ)'}
            }, status=400)

        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if file.content_type not in allowed_types:
            return JsonResponse({
                'error': {'message': 'Недопустимый тип файла. Разрешены: JPEG, PNG, GIF, WebP'}
            }, status=400)

        upload_path = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(upload_path, exist_ok=True)
        
        fs = FileSystemStorage(location=upload_path)
        filename = fs.save(file.name, file)
        file_url = f"{settings.MEDIA_URL}uploads/{filename}"

        return JsonResponse({
            'url': file_url
        })


class PopularPostsView(DataMixin, ListView):
    """Популярные статьи"""
    template_name = 'main/index.html'
    context_object_name = 'posts'
    title_page = 'Популярное'

    def get_queryset(self):
        return Post.published.all().order_by('-views')[:20]


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
            # Создаём уведомление для автора
            Notification.objects.create(
                recipient=author,
                sender=request.user,
                notification_type='follow',
                message=f'{request.user.username} подписался на вас'
            )
        
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

    def get_queryset(self):
        subscribed_authors = Subscription.objects.filter(
            subscriber=self.request.user
        ).values_list('author_id', flat=True)
        return Post.published.filter(author_id__in=subscribed_authors).order_by('-time_create')

# Обсуждения
class DiscussionsView(DataMixin, ListView):
    template_name = 'main/discussions.html'
    context_object_name = 'questions'
    title_page = 'Обсуждения | PageGlow'

    def get_queryset(self):
        return Post.published.all().select_related('cat', 'author')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    

class CreateDiscussionsView(DataMixin, CreateView):
    form_class = AddQuestionForm
    template_name = 'main/discussions_create.html'
    title_page = 'Начать обсуждение | PageGlow'

    def form_valid(self, form):
        return super().form_valid(form)
    
    def get_success_url(self):
            return reverse_lazy('main:discussion_detail')
    

@method_decorator(login_required, name='dispatch')
class NotificationsView(View):
    """Получение уведомлений"""
    def get(self, request, *args, **kwargs):
        notifications = Notification.objects.filter(
            recipient=request.user
        ).order_by('-created_at')[:20]
        
        unread_count = notifications.filter(is_read=False).count()
        
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
        'title': 'О платформе PageGlow',
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