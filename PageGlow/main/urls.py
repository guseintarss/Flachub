from django.contrib import admin
from django.urls import path

from . import views
from .feeds import LatestPostsFeed


urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('', views.MainHome.as_view(), name='home'),
    path('admin/', admin.site.urls, name='admin'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('search/', views.Search.as_view(), name='search'),
    path('login/', views.login, name='login'),
    path('addpage/', views.AddPage.as_view(), name='addpage'),
    
    # Обсуждения
    path('discussions/', views.DiscussionsView.as_view(), name='discussions'),
    path('discussions/create/', views.CreateDiscussionView.as_view(), name='create_discussion'),
    path('discussions/<int:pk>/', views.DiscussionDetailView.as_view(), name='discussion_detail'),
    path('ajax/discussions/add-comment/', views.AddDiscussionCommentAjaxView.as_view(), name='add_discussion_comment_ajax'),
    path('ajax/discussions/delete-comment/', views.DeleteDiscussionCommentAjaxView.as_view(), name='delete_discussion_comment_ajax'),
    path('ajax/discussions/close/', views.CloseDiscussionView.as_view(), name='close_discussion'),
    path('ajax/discussions/toggle-comment-like/', views.ToggleDiscussionCommentLikeView.as_view(), name='toggle_discussion_comment_like'),
    
    path('post/<slug:post_slug>/', views.ShowPost.as_view(), name='post'),
    path('category/<slug:cat_slug>/', views.MainCategory.as_view(), name='category'),
    path('tag/<slug:tag_slug>/', views.TagPostList.as_view(), name='tag'),
    path('edit/<slug:slug>/', views.UpdatePage.as_view(), name='edit_page'),
    path('ajax/like/', views.PostLikeAjaxView.as_view(), name='post_like_ajax'),
    path('ajax/favorite/', views.PostFavoriteAjaxView.as_view(), name='post_favorite_ajax'),
    path('ajax/add-comment/', views.AddCommentAjaxView.as_view(), name='add_comment_ajax'),
    path('ajax/delete-comment/', views.DeleteCommentAjaxView.as_view(), name='delete_comment_ajax'),

    path('upload/', views.CKEditorUploadView.as_view(), name='ckeditor_upload'),
    
    path('popular/', views.PopularPostsView.as_view(), name='popular'),
    path('feed/', views.SubscriptionFeedView.as_view(), name='subscription_feed'),
    path('ajax/subscribe/', views.SubscribeAuthorView.as_view(), name='subscribe_author'),
    path('ajax/notifications/', views.NotificationsView.as_view(), name='notifications'),
    path('ajax/notifications/read/', views.MarkNotificationsReadView.as_view(), name='mark_notifications_read'),
    path('rss/', LatestPostsFeed(), name='rss_feed'),
    
    # Информационные страницы
    path('about-us/', views.about_us, name='about_us'),
    path('terms/', views.terms_of_use, name='terms_of_use'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
]
