"""
Management команда для проверки и выдачи достижений существующим пользователям
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from main.models import Post, Comment, Bookmark, UserBadge, UserAchievement
from main.signals import check_and_award_badge
from django.db.models import Sum, Count

User = get_user_model()


class Command(BaseCommand):
    help = 'Проверить и выдать достижения всем пользователям'

    def handle(self, *args, **kwargs):
        self.stdout.write('Начинаю проверку достижений...')
        
        users = User.objects.all()
        total_awarded = 0
        
        for user in users:
            user_awarded = 0
            
            # Проверка бейджа за первую статью
            published_count = Post.objects.filter(author=user, is_published=True).count()
            if published_count >= 1:
                if not UserAchievement.objects.filter(user=user, badge__key='first_post').exists():
                    check_and_award_badge(
                        user=user,
                        badge_key='first_post',
                        badge_name='Первые шаги',
                        badge_description='Опубликована первая статья',
                        badge_icon='🌱',
                        badge_color='#4caf50',
                        reason='Первая опубликованная статья'
                    )
                    user_awarded += 1
            
            # Проверка бейджа за 10 статей
            if published_count >= 10:
                if not UserAchievement.objects.filter(user=user, badge__key='author').exists():
                    check_and_award_badge(
                        user=user,
                        badge_key='author',
                        badge_name='Автор',
                        badge_description='Опубликовано 10 статей',
                        badge_icon='✍️',
                        badge_color='#2196f3',
                        reason='10 опубликованных статей'
                    )
                    user_awarded += 1
            
            # Проверка бейджа за популярность (500+ просмотров)
            popular_posts = Post.objects.filter(author=user, is_published=True, views__gte=500).count()
            if popular_posts >= 1:
                if not UserAchievement.objects.filter(user=user, badge__key='expert').exists():
                    check_and_award_badge(
                        user=user,
                        badge_key='expert',
                        badge_name='Эксперт',
                        badge_description='Статья набрала 500+ просмотров',
                        badge_icon='🎓',
                        badge_color='#ff9800',
                        reason='Статья набрала 500 просмотров'
                    )
                    user_awarded += 1
            
            # Проверка бейджа за 1000+ просмотров суммарно
            total_views = Post.objects.filter(author=user, is_published=True).aggregate(
                total=Sum('views')
            )['total'] or 0
            if total_views >= 1000:
                if not UserAchievement.objects.filter(user=user, badge__key='popular_author').exists():
                    check_and_award_badge(
                        user=user,
                        badge_key='popular_author',
                        badge_name='Популярный автор',
                        badge_description='1000+ суммарных просмотров статей',
                        badge_icon='⭐',
                        badge_color='#e91e63',
                        reason='1000+ просмотров статей'
                    )
                    user_awarded += 1
            
            # Проверка бейджа за первый комментарий
            comment_count = Comment.objects.filter(author=user).count()
            if comment_count >= 1:
                if not UserAchievement.objects.filter(user=user, badge__key='first_comment').exists():
                    check_and_award_badge(
                        user=user,
                        badge_key='first_comment',
                        badge_name='Голос',
                        badge_description='Оставлен первый комментарий',
                        badge_icon='💬',
                        badge_color='#00bcd4',
                        reason='Первый комментарий'
                    )
                    user_awarded += 1
            
            # Проверка бейджа за 50 комментариев
            if comment_count >= 50:
                if not UserAchievement.objects.filter(user=user, badge__key='commentator').exists():
                    check_and_award_badge(
                        user=user,
                        badge_key='commentator',
                        badge_name='Комментатор',
                        badge_description='Оставлено 50 комментариев',
                        badge_icon='🗣️',
                        badge_color='#9c27b0',
                        reason='50 комментариев'
                    )
                    user_awarded += 1
            
            # Проверка бейджа за 10 закладок
            bookmark_count = Bookmark.objects.filter(user=user).count()
            if bookmark_count >= 10:
                if not UserAchievement.objects.filter(user=user, badge__key='collector').exists():
                    check_and_award_badge(
                        user=user,
                        badge_key='collector',
                        badge_name='Коллекционер',
                        badge_description='Собрано 10 закладок',
                        badge_icon='📚',
                        badge_color='#673ab7',
                        reason='10 закладок'
                    )
                    user_awarded += 1
            
            # Проверка бейджа за 50 закладок
            if bookmark_count >= 50:
                if not UserAchievement.objects.filter(user=user, badge__key='super_collector').exists():
                    check_and_award_badge(
                        user=user,
                        badge_key='super_collector',
                        badge_name='Супер коллекционер',
                        badge_description='Собрано 50 закладок',
                        badge_icon='📖',
                        badge_color='#3f51b5',
                        reason='50 закладок'
                    )
                    user_awarded += 1
            
            if user_awarded > 0:
                total_awarded += user_awarded
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {user.username}: выдано {user_awarded} достижений')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Всего выдано достижений: {total_awarded}')
        )
