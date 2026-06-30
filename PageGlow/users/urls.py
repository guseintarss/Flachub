from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import RuleViewSet

app_name = 'users'
router = DefaultRouter()
router.register(r'rules', RuleViewSet, basename='rule')

urlpatterns = [
    path('', include(router.urls)),
]
