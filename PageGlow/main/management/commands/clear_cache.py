"""
Management command для очистки кэша
Использование: python manage.py clear_cache
"""

from django.core.management.base import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):
    help = 'Очистка всего кэша'

    def add_arguments(self, parser):
        parser.add_argument(
            '--pattern',
            type=str,
            help='Шаблон для ключей (например: similar_posts_*)',
            default='*'
        )

    def handle(self, *args, **options):
        pattern = options['pattern']
        
        self.stdout.write(self.style.WARNING(f'Очистка кэша по шаблону: {pattern}'))
        
        if pattern == '*':
            # Полная очистка
            cache.clear()
            self.stdout.write(self.style.SUCCESS('✓ Кэш полностью очищен'))
        else:
            # Очистка по шаблону (требует django-redis)
            try:
                from django_redis import get_redis_connection
                conn = get_redis_connection("default")
                keys = conn.keys(pattern)
                if keys:
                    conn.delete(*keys)
                    self.stdout.write(self.style.SUCCESS(f'✓ Удалено {len(keys)} ключей'))
                else:
                    self.stdout.write(self.style.WARNING('Ключи не найдены'))
            except ImportError:
                self.stdout.write(self.style.ERROR(
                    'Для очистки по шаблону требуется django-redis'
                ))
                cache.clear()
                self.stdout.write(self.style.SUCCESS('✓ Кэш полностью очищен'))
        
        self.stdout.write(self.style.SUCCESS('✅ Готово!'))
