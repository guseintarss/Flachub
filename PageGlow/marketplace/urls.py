from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    # Маркетплейс главная
    path('', views.MarketplaceHomeView.as_view(), name='home'),
    
    # Проекты
    path('projects/', views.MarketplaceHomeView.as_view(), name='projects_list'),
    path('projects/<uuid:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('projects/create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('projects/<uuid:pk>/edit/', views.ProjectUpdateView.as_view(), name='project_edit'),
    path('projects/<uuid:pk>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),
    
    # Фрилансеры
    path('freelancers/', views.FreelancersListView.as_view(), name='freelancers_list'),
    path('freelancers/<slug:username>/', views.FreelancerProfileView.as_view(), name='freelancer_profile'),
    path('freelancers/<slug:username>/edit/', views.FreelancerProfileEditView.as_view(), name='freelancer_profile_edit'),
    
    # Профиль создание
    path('profile/freelancer/create/', views.CreateFreelancerProfileView.as_view(), name='create_freelancer_profile'),
    path('profile/company/create/', views.CreateCompanyProfileView.as_view(), name='create_company_profile'),
    
    # Предложения (ставки)
    path('projects/<uuid:project_id>/bid/', views.BidCreateView.as_view(), name='bid_create'),
    path('bids/<uuid:pk>/accept/', views.BidAcceptView.as_view(), name='bid_accept'),
    
    # Чат
    path('projects/<uuid:project_id>/chat/', views.project_chat_view, name='project_chat'),
    path('chat/<uuid:chat_id>/message/', views.send_message_view, name='send_message'),
    
    # Дашборды
    path('freelancer/dashboard/', views.freelancer_dashboard, name='freelancer_dashboard'),
    path('client/dashboard/', views.client_dashboard, name='client_dashboard'),
]
