"""
API для работы с подписками и подписчиками пользователей
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from .serializers import UserProfileSerializer

User = get_user_model()


class SubscriptionViewSet(viewsets.ViewSet):
    """
    API для управления подписками пользователя
    
    Endpoints:
    - GET /api/users/{id}/subscriptions/ - получить подписки пользователя
    - GET /api/users/{id}/subscribers/ - получить подписчиков пользователя
    - POST /api/users/{id}/subscribe/ - подписаться на пользователя
    - POST /api/users/{id}/unsubscribe/ - отписаться от пользователя
    - GET /api/users/{id}/is_subscribed/ - проверить подписку
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='(?P<user_id>[^/.]+)/subscriptions')
    def subscriptions(self, request, user_id=None):
        """Получить список подписок пользователя"""
        try:
            user = get_object_or_404(User, id=user_id)
            subscriptions = user.subscriptions.all()
            
            # Пагинация
            page = request.query_params.get('page', 1)
            limit = request.query_params.get('limit', 20)
            
            start = (int(page) - 1) * int(limit)
            end = start + int(limit)
            
            subscriptions_page = subscriptions[start:end]
            
            serializer = UserProfileSerializer(subscriptions_page, many=True)
            
            return Response({
                'count': subscriptions.count(),
                'results': serializer.data,
                'page': int(page),
                'limit': int(limit)
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'], url_path='(?P<user_id>[^/.]+)/subscribers')
    def subscribers(self, request, user_id=None):
        """Получить список подписчиков пользователя"""
        try:
            user = get_object_or_404(User, id=user_id)
            subscribers = user.subscribers.all()
            
            # Пагинация
            page = request.query_params.get('page', 1)
            limit = request.query_params.get('limit', 20)
            
            start = (int(page) - 1) * int(limit)
            end = start + int(limit)
            
            subscribers_page = subscribers[start:end]
            
            serializer = UserProfileSerializer(subscribers_page, many=True)
            
            return Response({
                'count': subscribers.count(),
                'results': serializer.data,
                'page': int(page),
                'limit': int(limit)
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'], url_path='(?P<user_id>[^/.]+)/subscribe')
    def subscribe(self, request, user_id=None):
        """Подписаться на пользователя"""
        try:
            target_user = get_object_or_404(User, id=user_id)
            current_user = request.user
            
            if target_user == current_user:
                return Response(
                    {'error': 'Вы не можете подписаться на себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Добавляем подписку
            current_user.subscribe_to(target_user)
            
            return Response({
                'message': 'Вы подписались на этого пользователя',
                'subscribed': True
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'], url_path='(?P<user_id>[^/.]+)/unsubscribe')
    def unsubscribe(self, request, user_id=None):
        """Отписаться от пользователя"""
        try:
            target_user = get_object_or_404(User, id=user_id)
            current_user = request.user
            
            # Удаляем подписку
            current_user.unsubscribe_from(target_user)
            
            return Response({
                'message': 'Вы отписались от этого пользователя',
                'subscribed': False
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'], url_path='(?P<user_id>[^/.]+)/is_subscribed')
    def is_subscribed(self, request, user_id=None):
        """Проверить, подписан ли текущий пользователь на целевого"""
        try:
            target_user = get_object_or_404(User, id=user_id)
            current_user = request.user
            
            is_subscribed = current_user.is_subscribed_to(target_user)
            
            return Response({
                'is_subscribed': is_subscribed,
                'target_user_id': target_user.id,
                'current_user_id': current_user.id
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserStatsViewSet(viewsets.ViewSet):
    """
    API для получения статистики пользователя
    
    Endpoints:
    - GET /api/users/{id}/stats/ - получить статистику пользователя
    """

    @action(detail=False, methods=['get'], url_path='(?P<user_id>[^/.]+)/stats')
    def stats(self, request, user_id=None):
        """Получить статистику пользователя"""
        try:
            user = get_object_or_404(User, id=user_id)
            
            stats = {
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'subscriptions_count': user.get_subscriptions_count(),
                'subscribers_count': user.get_subscribers_count(),
                'created_at': user.created_at,
                'updated_at': user.updated_at,
            }
            
            # Добавляем информацию о фрилансере если есть
            if hasattr(user, 'freelancer_profile'):
                profile = user.freelancer_profile
                stats['freelancer'] = {
                    'rating': float(profile.rating),
                    'total_projects': profile.total_projects,
                    'total_reviews': profile.total_reviews,
                    'is_verified': profile.is_verified,
                    'is_available': profile.is_available,
                }
            
            return Response(stats)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
