"""
Management command для оптимизации базы данных
Использование: python manage.py optimize_db
"""

from django.core.management.base import BaseCommand
from django.db import connection
from main.models import Post, Category, Comment


class Command(BaseCommand):
    help = 'Оптимизация базы данных: анализ таблиц и обновление статистики'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Оптимизация базы данных...'))
        
        # ANALYZE для обновления статистики
        self.stdout.write('📊 Обновление статистики таблиц...')
        
        tables = [
            'main_post',
            'main_category',
            'main_tagpost',
            'main_comment',
            'users_user',
        ]
        
        with connection.cursor() as cursor:
            for table in tables:
                cursor.execute(f'ANALYZE {table}')
                self.stdout.write(f'  ✓ {table}')
        
        # Проверка количества записей
        self.stdout.write('\n📈 Статистика:')
        self.stdout.write(f'  Постов: {Post.objects.count()}')
        self.stdout.write(f'  Категорий: {Category.objects.count()}')
        self.stdout.write(f'  Комментариев: {Comment.objects.count()}')
        self.stdout.write(f'  Просмотров (всего): {Post.objects.aggregate(total_views=Sum("views"))["total_views"] or 0:,}')
        
        # Проверка индексов
        self.stdout.write('\n🔍 Проверка индексов...')
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT indexname, indexdef 
                FROM pg_indexes 
                WHERE tablename = 'main_post'
                ORDER BY indexname;
            """)
            indexes = cursor.fetchall()
            for index_name, index_def in indexes:
                self.stdout.write(f'  ✓ {index_name}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Оптимизация завершена!'))


from django.db.models import Sum
