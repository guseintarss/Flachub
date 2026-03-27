from django.contrib.auth.views import LogoutView, PasswordChangeView, PasswordChangeDoneView, PasswordResetView, \
    PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import path, reverse_lazy, include

from rest_framework.routers import DefaultRouter

from main.views import PostDeleteView
# from main.views import PostDeleteView
from . import views
from .views import EditProfileUser, RuleViewSet

app_name = 'users'
router = DefaultRouter()
router.register(r'rules', RuleViewSet, basename='rule')

urlpatterns = [
    path('login/', views.LoginUser.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterUser.as_view(), name='register'),
    path('user/<int:user_id>/toggle-active/', views.delete_user, name='delete_user'),
    path('', include(router.urls)),
    path('profile/', views.profile_user, name='profile'),
    path('author/<str:username>/', views.author_profile, name='author_profile'),
    path('articles/<slug:slug>/delete/', PostDeleteView.as_view(), name='article-delete'),
    path('edit_profile/', views.EditProfileUser.as_view(), name='edit_profile'),

    # Система репутации
    path('reputation/history/', views.ReputationHistoryView.as_view(), name='reputation_history'),
    path('reputation/leaderboard/', views.ReputationLeaderboardView.as_view(), name='reputation_leaderboard'),
    path('reputation/user/<int:user_id>/add/', views.add_manual_reputation, name='add_reputation'),

    path('password_reset/', PasswordResetView.as_view(template_name='users/password_reset_form.html',
                                                            email_template_name='users/password_reset_email.html',
                                                      success_url=reverse_lazy("users:password_reset_done")
                                                      ), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('password_reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='users/password_reset_confirm.html',
        success_url=reverse_lazy("users:password_reset_complete"
                                 )), name='password_reset_confirm'),
    path('password_reset/complete/', PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'),


    path('password_change/', views.UserPasswordChange.as_view(), name='password_change'),
    path('password_change/done/', PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'), name='password_change_done'),
]


