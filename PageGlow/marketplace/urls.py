from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    # Маркетплейс главная есть
    path('', views.MarketplaceHomeView.as_view(), name='home'),
    
    # Проекты есть
    path('projects/', views.MarketplaceHomeView.as_view(), name='projects_list'),
    path('projects/<uuid:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('projects/create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('projects/<uuid:pk>/edit/', views.ProjectUpdateView.as_view(), name='project_edit'),
    path('projects/<uuid:pk>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),
    
    # Фрилансеры есть
    path('freelancers/', views.FreelancersListView.as_view(), name='freelancers_list'),
    path('freelancers/<slug:username>/', views.FreelancerProfileView.as_view(), name='freelancer_profile'),
    path('freelancers/<slug:username>/edit/', views.FreelancerProfileEditView.as_view(), name='freelancer_profile_edit'),
    
    # Профиль создание 
    path('profile/freelancer/create/', views.CreateFreelancerProfileView.as_view(), name='create_freelancer_profile'), # есть
    path('profile/company/create/', views.CreateCompanyProfileView.as_view(), name='create_company_profile'),
    
    # Предложения (ставки) есть
    path('projects/<uuid:project_id>/bid/', views.BidCreateView.as_view(), name='bid_create'),
    path('bids/<uuid:pk>/accept/', views.BidAcceptView.as_view(), name='bid_accept'),
    
    # Чат
    path('chats/', views.chats_list_view, name='chats_list'),
    path('chat/notifications/', views.get_chat_notifications, name='chat_notifications'),
    path('projects/<uuid:project_id>/chat/', views.project_chat_view, name='project_chat'),
    path('chat/<uuid:chat_id>/message/', views.send_message_view, name='send_message'),
    path('chat/<uuid:chat_id>/mark-read/', views.mark_messages_read_view, name='mark_messages_read'),
    path('chat/<uuid:chat_id>/messages-status/', views.get_messages_status_view, name='get_messages_status'),
    
    # Дашборды 
    path('freelancer/dashboard/', views.freelancer_dashboard, name='freelancer_dashboard'), # есть
    path('client/dashboard/', views.client_dashboard, name='client_dashboard'),
    
    # Справочные страницы есть
    path('how-it-works/', views.how_it_works, name='how_it_works'),
    path('publish-project/', views.publish_project_guide, name='publish_project_guide'),
    path('find-work/', views.find_work_guide, name='find_work_guide'),
    path('best-freelancers/', views.best_freelancers, name='best_freelancers'),
    path('categories/', views.categories_view, name='categories'),
    path('faq/', views.faq_view, name='faq'),
    path('about/', views.about_platform, name='about_platform'),
    path('terms/', views.terms_and_policy, name='terms_and_policy'),
    path('security/', views.security_view, name='security'),
    path('contact/', views.contact_us, name='contact_us'),
]
