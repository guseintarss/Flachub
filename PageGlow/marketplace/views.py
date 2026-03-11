import json
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.urls import reverse_lazy
from django.db.models import Q, Avg, Count
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from datetime import timedelta
from django.utils import timezone

from . import models, forms


# ===== MARKETPLACE HOME =====

class MarketplaceHomeView(ListView):
    """Главная страница маркетплейса"""
    template_name = 'marketplace/home.html'
    context_object_name = 'projects'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = models.Project.objects.filter(
            status=models.ProjectStatus.PUBLISHED
        ).select_related('client').prefetch_related('required_skills')
        
        # Фильтрация
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        difficulty = self.request.GET.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        search = self.request.GET.get('q')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search)
            )
        
        # Сортировка
        sort = self.request.GET.get('sort', '-created_at')
        if sort in ['created_at', '-created_at', 'deadline', 'budget_max']:
            queryset = queryset.order_by(sort)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Маркетплейс проектов'
        context['categories'] = dict(models.Project._meta.get_field('category').choices)
        context['difficulties'] = dict(models.Project._meta.get_field('difficulty').choices)
        return context


# ===== PROJECT VIEWS =====

class ProjectDetailView(DetailView):
    """Детальное описание проекта"""
    model = models.Project
    template_name = 'marketplace/project_detail.html'
    context_object_name = 'project'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        
        # Активные предложения
        context['bids'] = project.bids.filter(
            status=models.BidStatus.PENDING
        ).select_related('freelancer__freelancer_profile').order_by('-ai_score')
        
        # Чат проекта
        try:
            context['chat'] = project.chat
        except models.ProjectChat.DoesNotExist:
            context['chat'] = None
        
        # Проверка, может ли пользователь делать ставки
        context['can_bid'] = (
            self.request.user.is_authenticated and
            self.request.user != project.client and
            hasattr(self.request.user, 'freelancer_profile') and
            not project.bids.filter(freelancer=self.request.user).exists()
        )
        
        context['title'] = project.title
        return context


class ProjectCreateView(LoginRequiredMixin, CreateView):
    """Создание нового проекта"""
    model = models.Project
    form_class = forms.ProjectForm
    template_name = 'marketplace/project_form.html'
    
    def form_valid(self, form):
        form.instance.client = self.request.user
        response = super().form_valid(form)


        # Создаём чат проекта
        models.ProjectChat.objects.create(project=self.object)
        
        return response
    
    def get_success_url(self):
        return reverse_lazy('marketplace:project_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создать проект'
        return context


class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование проекта"""
    model = models.Project
    form_class = forms.ProjectForm
    template_name = 'marketplace/project_form.html'
    
    def test_func(self):
        return self.get_object().client == self.request.user
    
    def get_success_url(self):
        return reverse_lazy('marketplace:project_detail', kwargs={'pk': self.object.pk})


class ProjectDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление проекта"""
    model = models.Project
    template_name = 'marketplace/project_confirm_delete.html'
    success_url = reverse_lazy('marketplace:projects_list')
    
    def test_func(self):
        return self.get_object().client == self.request.user


# ===== FREELANCER PROFILE =====

class FreelancerProfileView(DetailView):
    """Профиль фрилансера"""
    model = models.FreelancerProfile
    template_name = 'marketplace/freelancer_profile.html'
    context_object_name = 'profile'
    slug_field = 'user__username'
    slug_url_kwarg = 'username'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()
        
        # Завершённые проекты (оптимизированный запрос с использованием aggregate)
        completed_count = models.Project.objects.filter(
            assigned_to=profile.user,
            status=models.ProjectStatus.COMPLETED
        ).aggregate(
            count=Count('id')
        )['count']
        context['completed_projects'] = completed_count
        
        # Отзывы
        context['reviews'] = models.Review.objects.filter(
            reviewed_user=profile.user
        ).select_related('reviewer').order_by('-created_at')[:5]
        
        # Процент завершения
        context['completion_rate'] = profile.get_completion_rate()
        
        context['title'] = f"Профиль {profile.user.get_full_name() or profile.user.username}"
        return context


class FreelancerProfileEditView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля фрилансера"""
    model = models.FreelancerProfile
    form_class = forms.FreelancerProfileForm
    template_name = 'marketplace/freelancer_profile_edit.html'
    
    def get_object(self):
        return self.request.user.freelancer_profile
    
    def test_func(self):
        return self.get_object().user == self.request.user
    
    def get_success_url(self):
        return reverse_lazy('marketplace:freelancer_profile', kwargs={'username': self.request.user.username})


class FreelancersListView(ListView):
    """Список всех фрилансеров"""
    model = models.FreelancerProfile
    template_name = 'marketplace/freelancers_list.html'
    context_object_name = 'freelancers'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = models.FreelancerProfile.objects.filter(
            is_verified=True,
            is_available=True
        ).select_related('user').prefetch_related('skills')
        
        # Фильтрация
        role = self.request.GET.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        min_rating = self.request.GET.get('min_rating')
        if min_rating:
            queryset = queryset.filter(rating__gte=float(min_rating))
        
        skill = self.request.GET.get('skill')
        if skill:
            queryset = queryset.filter(skills__slug=skill)
        
        search = self.request.GET.get('q')
        if search:
            queryset = queryset.filter(
                Q(user__username__icontains=search) |
                Q(bio__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search)
            )
        
        # Сортировка
        sort = self.request.GET.get('sort', '-rating')
        if sort in ['rating', '-rating', 'total_projects', '-total_projects']:
            queryset = queryset.order_by(sort)
        
        return queryset.order_by('-rating')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Фрилансеры'
        context['roles'] = dict(models.FreelancerRole.choices)
        context['all_skills'] = models.Skill.objects.all()
        return context


# ===== BID VIEWS =====

class BidCreateView(LoginRequiredMixin, CreateView):
    """Создание предложения на проект"""
    model = models.Bid
    form_class = forms.BidForm
    template_name = 'marketplace/bid_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Проверяем, что это фрилансер
        if not hasattr(request.user, 'freelancer_profile'):
            return HttpResponseForbidden('Only freelancers can submit bids')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(models.Project, pk=self.kwargs['project_id'])
        context['title'] = 'Подать предложение'
        return context
    
    def form_valid(self, form):
        form.instance.freelancer = self.request.user
        form.instance.project_id = self.kwargs['project_id']
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('marketplace:project_detail', kwargs={'pk': self.kwargs['project_id']})


class BidAcceptView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Принять предложение"""
    model = models.Bid
    fields = []
    
    def test_func(self):
        bid = self.get_object()
        return bid.project.client == self.request.user
    
    def post(self, request, *args, **kwargs):
        bid = self.get_object()
        
        # Отклоняем все остальные предложения
        bid.project.bids.exclude(id=bid.id).update(status=models.BidStatus.REJECTED)
        
        # Принимаем это предложение
        bid.status = models.BidStatus.ACCEPTED
        bid.save()
        
        # Обновляем статус проекта
        bid.project.status = models.ProjectStatus.IN_PROGRESS
        bid.project.assigned_to = bid.freelancer
        bid.project.save()
        
        return redirect('marketplace:project_detail', pk=bid.project.pk)


# ===== CHAT VIEWS =====

@login_required
def project_chat_view(request, project_id):
    """Чат проекта"""
    project = get_object_or_404(models.Project, pk=project_id)
    
    # Проверяем, что пользователь участник проекта
    if request.user != project.client and request.user != project.assigned_to:
        return HttpResponseForbidden('You are not a participant in this project')
    
    # Получаем или создаём чат
    chat, _ = models.ProjectChat.objects.get_or_create(project=project)
    
    messages = chat.messages.select_related('sender').order_by('created_at')
    
    context = {
        'title': f"Чат проекта: {project.title}",
        'project': project,
        'chat': chat,
        'messages': messages,
    }
    
    return render(request, 'marketplace/project_chat.html', context)


@login_required
@require_http_methods(["POST"])
def send_message_view(request, chat_id):
    """Отправить сообщение в чат"""
    chat = get_object_or_404(models.ProjectChat, pk=chat_id)
    
    # Проверяем права
    if (request.user != chat.project.client and 
        request.user != chat.project.assigned_to):
        return HttpResponseForbidden('You are not a participant in this project')
    
    content = request.POST.get('content', '').strip()
    embedded_url = request.POST.get('embedded_url', '').strip()
    embedded_type = request.POST.get('embedded_type', '')
    
    if not content:
        return JsonResponse({'error': 'Message cannot be empty'}, status=400)
    
    message = models.ChatMessage.objects.create(
        chat=chat,
        sender=request.user,
        content=content,
        embedded_url=embedded_url if embedded_url else None,
        embedded_type=embedded_type if embedded_type else None
    )
    
    return JsonResponse({
        'id': str(message.id),
        'sender': request.user.username,
        'content': message.content,
        'created_at': message.created_at.isoformat(),
    })


# ===== DASHBOARD VIEWS =====

@login_required
def freelancer_dashboard(request):
    """Дашборд фрилансера"""
    if not hasattr(request.user, 'freelancer_profile'):
        return redirect('marketplace:create_freelancer_profile')

    profile = request.user.freelancer_profile

    # Статистика
    bids_count = models.Bid.objects.filter(freelancer=request.user).count()
    accepted_bids = models.Bid.objects.filter(
        freelancer=request.user,
        status=models.BidStatus.ACCEPTED
    ).count()
    completed_projects = models.Project.objects.filter(
        assigned_to=request.user,
        status=models.ProjectStatus.COMPLETED
    ).count()

    # Активные проекты
    active_projects = models.Project.objects.filter(
        assigned_to=request.user,
        status__in=[models.ProjectStatus.IN_PROGRESS, models.ProjectStatus.REVIEW]
    ).select_related('client')

    # Доступные проекты с высокой совместимостью
    all_projects = models.Project.objects.filter(
        status=models.ProjectStatus.PUBLISHED
    ).select_related('client').prefetch_related('required_skills')

    recommended_projects = []
    for project in all_projects[:20]:
        # Передаём профиль фрилансера в метод расчёта совместимости
        score = project.ai_matching_score(profile)
        if score >= 70:
            recommended_projects.append({
                'project': project,
                'score': score
            })

    # Сортируем по убыванию баллов и берём топ‑5
    recommended_projects = sorted(
        recommended_projects,
        key=lambda x: x['score'],
        reverse=True
    )[:5]

    context = {
        'title': 'Дашборд фрилансера',
        'profile': profile,
        'bids_count': bids_count,
        'accepted_bids': accepted_bids,
        'completed_projects': completed_projects,
        'active_projects': active_projects,
        'recommended_projects': recommended_projects,
    }

    return render(request, 'marketplace/freelancer_dashboard.html', context)




@login_required
def client_dashboard(request):
    """Дашборд заказчика"""
    if not hasattr(request.user, 'company_profile'):
        return redirect('marketplace:create_company_profile')
    
    # Проекты клиента
    projects = models.Project.objects.filter(client=request.user).select_related('assigned_to')
    
    # Статистика
    total_spent = sum(
        project.bids.filter(status=models.BidStatus.ACCEPTED).values_list('proposed_price', flat=True)
        for project in projects
    )
    
    context = {
        'title': 'Дашборд заказчика',
        'projects': projects,
        'total_spent': total_spent,
        'completed_projects': projects.filter(status=models.ProjectStatus.COMPLETED).count(),
        'active_projects': projects.filter(status__in=[
            models.ProjectStatus.IN_PROGRESS,
            models.ProjectStatus.REVIEW
        ]).count(),
    }
    
    return render(request, 'marketplace/client_dashboard.html', context)


# ===== PROFILE SETUP VIEWS =====

class CreateFreelancerProfileView(LoginRequiredMixin, CreateView):
    """Создание профиля фрилансера"""
    model = models.FreelancerProfile
    form_class = forms.FreelancerProfileForm
    template_name = 'marketplace/create_freelancer_profile.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('marketplace:freelancer_dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создать профиль фрилансера'
        return context


class CreateCompanyProfileView(LoginRequiredMixin, CreateView):
    """Создание профиля компании"""
    model = models.CompanyProfile
    form_class = forms.CompanyProfileForm
    template_name = 'marketplace/create_company_profile.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('marketplace:client_dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создать профиль компании'
        return context




# ===== СПРАВОЧНЫЕ СТРАНИЦЫ =====

def how_it_works(request):
    """Как это работает"""
    context = {
        'title': 'Как это работает',
    }
    return render(request, 'marketplace/how_it_works.html', context)


def publish_project_guide(request):
    """Руководство: Как опубликовать проект"""
    context = {
        'title': 'Как опубликовать проект',
    }
    return render(request, 'marketplace/publish_guide.html', context)


def find_work_guide(request):
    """Руководство: Как найти работу"""
    context = {
        'title': 'Как найти работу',
    }
    return render(request, 'marketplace/find_work_guide.html', context)


def best_freelancers(request):
    """Лучшие фрилансеры"""
    context = {
        'title': 'Лучшие фрилансеры',
        'freelancers': models.FreelancerProfile.objects.filter(
            is_verified=True,
            is_available=True
        ).select_related('user').order_by('-rating')[:20]
    }
    return render(request, 'marketplace/best_freelancers.html', context)


def categories_view(request):
    """Категории проектов"""
    context = {
        'title': 'Категории',
        'categories': [
            {'name': 'Веб-разработка', 'value': 'web'},
            {'name': 'Мобильное приложение', 'value': 'mobile'},
            {'name': 'Data Science', 'value': 'data'},
            {'name': 'DevOps', 'value': 'devops'},
            {'name': 'Дизайн', 'value': 'design'},
            {'name': 'Другое', 'value': 'other'},
        ]
    }
    return render(request, 'marketplace/categories.html', context)


def faq_view(request):
    """Часто задаваемые вопросы"""
    context = {
        'title': 'Часто задаваемые вопросы',
        'faqs': [
            {
                'question': 'Как начать работу на платформе?',
                'answer': 'Зарегистрируйтесь, создайте профиль и приступайте к поиску работы или публикации проектов.'
            },
            {
                'question': 'Какая комиссия платформы?',
                'answer': 'Комиссия составляет 10% от стоимости проекта для фрилансеров и 5% для клиентов.'
            },
            {
                'question': 'Как защищены мои платежи?',
                'answer': 'Мы используем защищённую систему депонирования средств. Оплата переводится фрилансеру только после приёмки работы.'
            },
            {
                'question': 'Могу ли я отменить договор?',
                'answer': 'Да, вы можете отменить договор в течение 14 дней. Подробные условия указаны в соглашении.'
            },
            {
                'question': 'Как связаться с поддержкой?',
                'answer': 'Напишите нам на support@pageglow.ru или используйте форму обратной связи на сайте.'
            },
        ]
    }
    return render(request, 'marketplace/faq.html', context)


def about_platform(request):
    """О платформе"""
    context = {
        'title': 'О платформе PageGlow',
    }
    return render(request, 'marketplace/about_platform.html', context)


def terms_and_policy(request):
    """Правила и политика"""
    context = {
        'title': 'Правила и политика',
    }
    return render(request, 'marketplace/terms_and_policy.html', context)


def security_view(request):
    """Безопасность"""
    context = {
        'title': 'Безопасность на платформе',
    }
    return render(request, 'marketplace/security.html', context)


def contact_us(request):
    """Контакты"""
    context = {
        'title': 'Контакты',
        'email': 'support@pageglow.ru',
        'phone': '+7 (999) 999-99-99',
        'address': 'Москва, Россия',
    }
    return render(request, 'marketplace/contact.html', context)
