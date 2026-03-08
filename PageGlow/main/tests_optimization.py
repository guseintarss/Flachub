"""
Тесты для проверки оптимизаций
Проверяет количество запросов и производительность
"""

from django.test import TestCase, TransactionTestCase
from django.test.utils import CaptureQueriesContext
from django.db import connection
from main.models import Post, Comment, Subscription, Notification, Category
from users.models import User
from main.optimized_queries import OptimizedQueries
from main.cache_utils import get_author_stats, get_popular_posts


class DatabaseOptimizationTests(TransactionTestCase):
    """Тесты для проверки оптимизации запросов к БД"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        cls.author = User.objects.create_user(
            username='author',
            email='author@example.com',
            password='testpass123'
        )
        cls.category = Category.objects.create(name='Test Category')
    
    def setUp(self):
        """Создаём тестовые данные перед каждым тестом"""
        self.post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            content='Test content',
            cat=self.category,
            author=self.author,
            is_published=True
        )
        
        # Добавим комментарии
        for i in range(5):
            Comment.objects.create(
                post=self.post,
                author=self.user,
                content=f'Comment {i}'
            )
        
        # Добавим лайки
        self.post.likes.add(self.user)
    
    def test_get_posts_list_query_count(self):
        """Проверяем, что get_posts_list минимизирует запросы"""
        with CaptureQueriesContext(connection) as context:
            posts = list(OptimizedQueries.get_posts_list(limit=10))
            
            # Должно быть максимум 3-4 запроса:
            # 1. Select posts with select_related
            # 2. Prefetch tags
            # 3. Prefetch comments
            # 4. Prefetch likes/favorites
            query_count = len(context.captured_queries)
            
            print(f"\n✅ get_posts_list: {query_count} queries")
            self.assertLess(query_count, 5, 
                f"get_posts_list должна выполнять не более 4 запросов, получено {query_count}")
    
    def test_post_detail_query_count(self):
        """Проверяем оптимизацию детали поста"""
        with CaptureQueriesContext(connection) as context:
            post = OptimizedQueries.get_post_detail(self.post.slug)
            # Доступ к связанным объектам
            _ = post.author.username
            _ = post.cat.name
            _ = list(post.comments.all())
            
            query_count = len(context.captured_queries)
            print(f"\n✅ get_post_detail: {query_count} queries")
            self.assertLess(query_count, 5)
    
    def test_subscription_feed_query_count(self):
        """Проверяем оптимизацию ленты подписок"""
        # Создаём подписку
        Subscription.objects.create(
            subscriber=self.user,
            author=self.author
        )
        
        with CaptureQueriesContext(connection) as context:
            posts = list(OptimizedQueries.get_subscription_feed(self.user, limit=10))
            
            query_count = len(context.captured_queries)
            print(f"\n✅ get_subscription_feed: {query_count} queries")
            self.assertLess(query_count, 5)
    
    def test_cache_author_stats(self):
        """Проверяем кэширование статистики автора"""
        # Первый вызов - идёт в БД
        with CaptureQueriesContext(connection) as context:
            stats1 = get_author_stats(self.author.id, use_cache=False)
            first_query_count = len(context.captured_queries)
        
        # Второй вызов - из кэша
        with CaptureQueriesContext(connection) as context:
            stats2 = get_author_stats(self.author.id, use_cache=True)
            cached_query_count = len(context.captured_queries)
        
        print(f"\n✅ Author stats - first: {first_query_count} queries, cached: {cached_query_count} queries")
        
        # Кэшированный должен выполнить 0 запросов к БД
        self.assertEqual(cached_query_count, 0, "Кэшированный запрос должен быть без БД запросов")
        
        # Результаты должны быть одинаковы
        self.assertEqual(stats1, stats2)
    
    def test_cache_popular_posts(self):
        """Проверяем кэширование популярных постов"""
        # Увеличиваем views
        self.post.views = 100
        self.post.save()
        
        with CaptureQueriesContext(connection) as context:
            posts1 = get_popular_posts(use_cache=False)
            first_count = len(context.captured_queries)
        
        with CaptureQueriesContext(connection) as context:
            posts2 = get_popular_posts(use_cache=True)
            cached_count = len(context.captured_queries)
        
        print(f"\n✅ Popular posts - first: {first_count} queries, cached: {cached_count} queries")
        self.assertEqual(cached_count, 0, "Кэшированные популярные посты должны быть без запросов")


class QueryOptimizationTests(TestCase):
    """Тесты для проверки правильности оптимизированных запросов"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Создаём тестовых пользователей
        cls.users = [
            User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@test.com',
                password='pass'
            )
            for i in range(3)
        ]
        
        cls.category = Category.objects.create(name='Tech')
        
        # Создаём посты
        cls.posts = [
            Post.objects.create(
                title=f'Post {i}',
                slug=f'post-{i}',
                content=f'Content {i}',
                cat=cls.category,
                author=cls.users[0],
                is_published=True,
                views=i * 10
            )
            for i in range(5)
        ]
    
    def test_posts_list_returns_correct_data(self):
        """Проверяем, что оптимизированный запрос возвращает правильные данные"""
        posts = list(OptimizedQueries.get_posts_list())
        
        self.assertEqual(len(posts), 5)
        self.assertTrue(all(p.is_published for p in posts))
        self.assertTrue(all(p.cat is not None for p in posts))
    
    def test_popular_posts_ordering(self):
        """Проверяем сортировку популярных постов"""
        popular = OptimizedQueries.get_popular_posts(limit=5)
        
        views = [p['views'] for p in popular]
        self.assertEqual(views, sorted(views, reverse=True))
    
    def test_search_posts(self):
        """Проверяем поиск постов"""
        results = OptimizedQueries.search_posts('Post 1')
        
        self.assertEqual(len(results), 1)
        self.assertIn('Post 1', results.first().title)
    
    def test_comments_optimized(self):
        """Проверяем, что комментарии загружаются оптимально"""
        post = self.posts[0]
        
        # Создаём комментарии
        for i in range(3):
            Comment.objects.create(
                post=post,
                author=self.users[1],
                content=f'Comment {i}'
            )
        
        comments = OptimizedQueries.get_comments_for_post(post)
        
        self.assertEqual(len(comments), 3)
        self.assertTrue(all(c.author is not None for c in comments))


class PerformanceTests(TestCase):
    """Тесты производительности"""
    
    def test_large_dataset_performance(self):
        """Проверяем производительность на большом наборе данных"""
        from django.test.utils import override_settings
        from django.utils import timezone
        
        # Создаём большой набор данных
        category = Category.objects.create(name='Large')
        author = User.objects.create_user(
            username='large_author',
            email='large@test.com',
            password='pass'
        )
        
        # 100 постов
        posts = [
            Post(
                title=f'Post {i}',
                slug=f'post-large-{i}',
                content=f'Content {i}' * 100,
                cat=category,
                author=author,
                is_published=True,
                views=i
            )
            for i in range(100)
        ]
        Post.objects.bulk_create(posts)
        
        # Тест производительности
        import time
        
        start = time.time()
        posts = list(OptimizedQueries.get_posts_list(limit=50))
        end = time.time()
        
        execution_time = (end - start) * 1000  # в миллисекундах
        
        print(f"\n✅ Время загрузки 50 постов: {execution_time:.2f}ms")
        
        # Должно выполниться быстро (< 500ms для 50 постов)
        self.assertLess(execution_time, 500,
            f"Загрузка 50 постов должна быть быстрой, заняло {execution_time:.2f}ms")


# Дополнительные утилиты для тестирования
def print_query_stats(queries):
    """Выводит статистику запросов"""
    print(f"\nВсего запросов: {len(queries)}")
    
    queries_by_table = {}
    for q in queries:
        # Пытаемся извлечь название таблицы
        sql = q['sql']
        for table in ['main_post', 'main_comment', 'main_subscription', 'auth_user']:
            if table in sql:
                queries_by_table[table] = queries_by_table.get(table, 0) + 1
    
    for table, count in queries_by_table.items():
        print(f"  {table}: {count} запросов")
