from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db import connection
from PageGlow import settings
from main.views import page_not_found, CKEditorUploadView, server_error, bad_gateway, service_unavailable, permission_denied
from .sitemaps import (
    PostSitemap, StaticViewSitemap, CategorySitemap,
    TagSitemap, UserSitemap
)
from django.contrib.sitemaps.views import sitemap

from rest_framework.routers import DefaultRouter
from users.views import RuleViewSet


def health_check(request):
    status = {"status": "ok", "version": "3.0"}
    http_code = 200

    try:
        connection.ensure_connection()
        status["database"] = "ok"
    except Exception as e:
        status["database"] = f"error: {str(e)}"
        http_code = 503

    return JsonResponse(status, status=http_code)


router = DefaultRouter()
router.register(r'rules', RuleViewSet, basename='rule')

# Карта сайта
sitemaps = {
    'static': StaticViewSitemap,
    'posts': PostSitemap,
    'categories': CategorySitemap,
    'tags': TagSitemap,
    'users': UserSitemap,
}

urlpatterns = [
    path('health/', health_check, name='health'),
    path('admin/', admin.site.urls),
    path('',include("main.urls")),
    path('users/',include("users.urls", namespace='users')),
]

# Отключаем debug_toolbar для ASGI
import sys
IS_ASGI = 'daphne' in sys.argv[0] or 'uvicorn' in sys.argv[0]

if not IS_ASGI:
    urlpatterns.extend([
        path("__debug__/", include("debug_toolbar.urls")),
    ])

urlpatterns.extend([
    # Наш кастомный upload для CKEditor (должен быть перед django_ckeditor_5.urls)
    path('ckeditor5/image_upload/', CKEditorUploadView.as_view(), name='ckeditor_image_upload'),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain"), name="robots"),
])

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static('/ckeditor5/', document_root=settings.BASE_DIR / 'ckeditor5')

handler404 = page_not_found
handler500 = server_error
handler502 = bad_gateway
handler503 = service_unavailable
handler403 = permission_denied

admin.site.site_header = 'Панель администрирования'
