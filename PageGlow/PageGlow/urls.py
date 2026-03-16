from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from PageGlow import settings
from main.views import page_not_found, CKEditorUploadView
from .sitemaps import (
    PostSitemap, StaticViewSitemap, CategorySitemap, 
    TagSitemap, UserSitemap, DiscussionsSitemap
)
from django.contrib.sitemaps.views import sitemap

from rest_framework.routers import DefaultRouter
from users.views import RuleViewSet

router = DefaultRouter()
router.register(r'rules', RuleViewSet, basename='rule')

# Карта сайта
sitemaps = {
    'static': StaticViewSitemap,
    'posts': PostSitemap,
    'categories': CategorySitemap,
    'tags': TagSitemap,
    'users': UserSitemap,
    'discussions': DiscussionsSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include("main.urls")),
    path('users/',include("users.urls", namespace='users')),
    path('marketplace/', include("marketplace.urls", namespace='marketplace')),
    path("__debug__/", include("debug_toolbar.urls")),
    # Наш кастомный upload для CKEditor (должен быть перед django_ckeditor_5.urls)
    path('ckeditor5/image_upload/', CKEditorUploadView.as_view(), name='ckeditor_image_upload'),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static('/ckeditor5/', document_root=settings.BASE_DIR / 'ckeditor5')

handler404 = page_not_found

admin.site.site_header = 'Панель администрирования'

