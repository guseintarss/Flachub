

from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import HttpResponseForbidden, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, CreateView, UpdateView, DeleteView, ListView
from django.contrib import messages

from rest_framework import viewsets, permissions

from PageGlow import settings
from main.models import Discussion, Post
from main.utils import DataMixin
from users.forms import LoginUserForm, RegisterUserForm, ProfileUserForm, UserPasswordChangeForm
from users.models import User, Rule
from .serializers import RuleSerializer



class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'
    extra_context = {'title': 'Авторизация'}

    def user_detail(request, user_id):
        try:
            user = User.objects.get(id=user_id)
            if not user.is_active:
                return HttpResponseForbidden("Пользователь неактивен")
        except User.DoesNotExist:
            raise Http404("Пользователь не найден")

@login_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        confirm = request.POST.get('confirm', '').strip().lower()

        confirm_options = ['y', 'да', 'Подтверждаю','yes', 'удалить', 'delete']
        if confirm not in confirm_options:
            messages.error(request, 'Для удаления аккаунта необходимо подтверждение. Введите "да" или "удалить".')
            # Возвращаем на страницу подтверждения
            extra_context = {
                'title': 'Подтверждение удаления аккаунта',
                'default_image': settings.DEFAULT_USER_IMAGE,
                'user': user,
            }
            return render(request, 'users/delete_user.html', extra_context)
        try:
            user.is_active = False
            user.save()
            messages.success(request, f'Пользователь {user.username} успешно деактивирован.')

            if request.user.id == user_id:
                from django.contrib.auth import logout
                logout(request)
                return redirect('users:login')
            return redirect('users:register')

        except Exception as e:
            messages.error(request, f'Произошла ошибка при деактивации: {str(e)}')
            extra_context = {
                'title': 'Подтверждение удаления аккаунта',
                'default_image': settings.DEFAULT_USER_IMAGE,
                'user': user,
            }
            return render(request, 'users/delete_user.html', extra_context)

    extra_context = {
        'title': 'Подтверждение удаления аккаунта',
        'default_image': settings.DEFAULT_USER_IMAGE,
        'user': user,
    }
    return render(request, 'users/delete_user.html', extra_context)

# def get_success_url(self):
#     return reverse_lazy('home')

class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'users/register.html'
    extra_context = {'title': 'Регистрация'}
    success_url = reverse_lazy('users:login')

class EditProfileUser(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = ProfileUserForm
    template_name = 'users/edit_profile.html'
    extra_context = {
        'title':'Редактирование пользователя',
        'default_image': settings.DEFAULT_USER_IMAGE,
    }

    def get_success_url(self):
        return reverse_lazy('users:edit_profile')

    def get_object(self, queryset=None):
        return self.request.user
    
    def form_valid(self, form):
        # Обрабатываем дату рождения если она есть
        if form.cleaned_data.get('data_birth'):
            from datetime import datetime
            data_birth = form.cleaned_data['data_birth']
            if isinstance(data_birth, str):
                try:
                    data_birth = datetime.strptime(data_birth, '%Y-%m-%d').date()
                except ValueError:
                    try:
                        data_birth = datetime.strptime(data_birth, '%d.%m.%Y').date()
                    except ValueError:
                        form.add_error('data_birth', 'Неверный формат даты')
                        return self.form_invalid(form)
            form.instance.data_birth = data_birth
        
        # Обрабатываем телефон
        if form.cleaned_data.get('phone_namber'):
            phone = form.cleaned_data['phone_namber']
            # Очищаем от форматирования, оставляем только цифры
            cleaned = ''.join(filter(lambda x: x.isdigit(), phone))
            
            # Если номер начинается с 8, заменяем на 7
            if cleaned.startswith('8'):
                cleaned = '7' + cleaned[1:]
            
            # Если не начинается с 7, добавляем 7
            if not cleaned.startswith('7'):
                cleaned = '7' + cleaned
            
            # Ограничиваем 11 цифрами
            form.instance.phone_namber = cleaned[:11]

        return super().form_valid(form)


@login_required
def profile_user(request):
    post_data = request.user.posts.select_related('author', 'cat').all()

    if post_data == 'published':
        return Post.objects.filter(is_published=True).order_by('-created')
    elif post_data == 'drafts':
        return Post.objects.filter(is_published=False).order_by('-created')

    user = request.user

    # Опубликованные посты (используем кастомный менеджер)
    published_posts = Post.published.filter(author=user).select_related('cat', 'author').annotate(likes_count=Count('likes', distinct=True))

    # Черновики (is_published = DRAFT)
    drafts = Post.objects.filter(
        author=user,
        is_published=Post.Status.DRAFT
    ).select_related('cat', 'author').annotate(likes_count=Count('likes', distinct=True))

    # Избранные посты (используем ManyToMany поле 'favorites')
    favorites = Post.objects.filter(
        favorites=user  # Посты, где текущий пользователь в списке избранных
    ).select_related('cat', 'author').annotate(likes_count=Count('likes', distinct=True))

    discussions_data = Discussion.objects.filter(
        author = user,
    ).prefetch_related('tags').select_related('author', 'cat')

    extra_context = {
        'title': 'Профиль пользователя',
        'default_image': settings.DEFAULT_USER_IMAGE,
        'posts': post_data,
        'published_posts': published_posts,
        'drafts': drafts,
        'favorites': favorites,
        'discussion_dis': discussions_data,
        'user': user,
    }
    return render(request, 'users/profile.html', extra_context)

class UserPasswordChange(PasswordChangeView):
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy('users:password_change_done')
    template_name = 'users/password_change_form.html'


def author_profile(request, username):
    """Публичный профиль автора - только просмотр статей"""
    from main.models import Subscription
    from django.db.models import Count

    author = get_object_or_404(User, username=username, is_active=True)

    # Оптимизированный запрос с подсчётом подписок
    published_posts = Post.published.filter(
        author=author
    ).select_related('cat', 'author').prefetch_related('tags').annotate(
        likes_count=Count('likes', distinct=True)
    ).order_by('-time_create')
    
    # Подсчитываем подписки в одном запросе с использованием Count
    subscription_stats = Subscription.objects.filter(
        author=author
    ).aggregate(
        subscribers_count=Count('id')
    )
    subscribers_count = subscription_stats['subscribers_count']
    
    # Подсчитываем подписки пользователя в одном запросе
    subscriptions = Subscription.objects.filter(
        subscriber=author
    ).aggregate(
        subscriptions_count=Count('id')
    )
    subscriptions_count = subscriptions['subscriptions_count']
    
    is_subscribed = False
    if request.user.is_authenticated and request.user != author:
        is_subscribed = Subscription.objects.filter(subscriber=request.user, author=author).exists()
    
    extra_context = {
        'title': f'Профиль {author.username}',
        'author': author,
        'default_image': settings.DEFAULT_USER_IMAGE,
        'published_posts': published_posts,
        'is_own_profile': request.user == author if request.user.is_authenticated else False,
        'subscribers_count': subscribers_count,
        'subscriptions_count': subscriptions_count,
        'is_subscribed': is_subscribed,
    }
    return render(request, 'users/author_profile.html', extra_context)


# def deactivate_user(request):
#     user = User.objects.get(id=request.user.id)
#     user.is_active=False
#     user.save()
#     return render(request, 'users/deactivate_user.html')

class RuleViewSet(viewsets.ModelViewSet):
    queryset = Rule.objects.all()
    serializer_class = RuleSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()