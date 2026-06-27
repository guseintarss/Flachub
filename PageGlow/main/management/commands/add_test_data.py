from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Добавляет тестовые данные в БД'

    def handle(self, *args, **options):
        from main.models import Post, Category, TagPost, Comment

        self.stdout.write('Добавляю тестовые данные...')

        Comment.objects.all().delete()
        Post.objects.all().delete()
        Category.objects.all().delete()
        TagPost.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write('  Старые данные очищены')

        # Категории
        cat_names = ['Python', 'JavaScript', 'Backend', 'Frontend', 'DevOps', 'Базы данных', 'Алгоритмы', 'Дизайн']
        categories = {}
        for name in cat_names:
            cat = Category.objects.create(name=name)
            categories[name.lower()] = cat
        self.stdout.write(f'  Создано {len(categories)} категорий')

        # Теги
        tag_names = ['django', 'react', 'docker', 'python', 'javascript', 'postgresql',
                     'linux', 'api', 'testing', 'git', 'fastapi', 'typescript', 'css',
                     'html', 'redis', 'sql', 'algorithms', 'design', 'database']
        tags = {}
        for name in tag_names:
            tag = TagPost.objects.create(tag=name, slug=name)
            tags[name] = tag
        self.stdout.write(f'  Создано {len(tags)} тегов')

        # Пользователи
        users_data = [
            ('alex_dev', 'alex@example.com'),
            ('maria_coder', 'maria@example.com'),
            ('ivan_admin', 'ivan@example.com'),
            ('olga_devops', 'olga@example.com'),
            ('dmitry_front', 'dmitry@example.com'),
        ]
        users = {}
        for username, email in users_data:
            user = User.objects.create_user(username=username, email=email, password='testpass123', is_active=True)
            users[username] = user
        self.stdout.write(f'  Создано {len(users)} пользователей')

        # Посты
        now = timezone.now()
        posts_list = [
            {
                'title': 'Введение в Django Rest Framework',
                'cat': 'backend',
                'content': '<h2>Что такое Django Rest Framework?</h2><p>Django Rest Framework (DRF) — это мощный инструмент для создания REST API. Он предоставляет сериализацию, аутентификацию, пагинацию и многое другое.</p><h3>Установка</h3><pre><code>pip install djangorestframework</code></pre>',
                'author': 'alex_dev',
                'tags': ['django', 'python', 'api'],
            },
            {
                'title': 'React Hooks: полное руководство',
                'cat': 'frontend',
                'content': '<h2>React Hooks</h2><p>Хуки позволяют использовать состояние и другие возможности React в функциональных компонентах. Представлены в React 16.8.</p><h3>useState</h3><p>Базовый хук для управления состоянием.</p>',
                'author': 'maria_coder',
                'tags': ['react', 'javascript', 'typescript'],
            },
            {
                'title': 'Docker для начинающих',
                'cat': 'devops',
                'content': '<h2>Что такое Docker?</h2><p>Платформа для разработки и запуска приложений в контейнерах.</p><ul><li>Образ (Image) — шаблон контейнера</li><li>Контейнер — запущенный экземпляр</li><li>Dockerfile — инструкция сборки</li></ul>',
                'author': 'olga_devops',
                'tags': ['docker', 'linux'],
            },
            {
                'title': 'Оптимизация PostgreSQL запросов',
                'cat': 'базы данных',
                'content': '<h2>Оптимизация запросов</h2><p>PostgreSQL предоставляет мощные инструменты для оптимизации.</p><h3>Индексы</h3><p>B-tree, Hash, GiST, GIN — основные типы индексов.</p>',
                'author': 'ivan_admin',
                'tags': ['postgresql', 'sql', 'database'],
            },
            {
                'title': 'Алгоритмы сортировки: сравнительный анализ',
                'cat': 'алгоритмы',
                'content': '<h2>Сравнение алгоритмов</h2><h3>QuickSort</h3><p>Средняя сложность O(n log n).</p><h3>MergeSort</h3><p>Стабильная сортировка O(n log n).</p>',
                'author': 'dmitry_front',
                'tags': ['algorithms', 'python'],
            },
            {
                'title': 'CI/CD с GitHub Actions',
                'cat': 'devops',
                'content': '<h2>Настройка CI/CD</h2><p>GitHub Actions автоматизирует сборку, тестирование и деплой.</p>',
                'author': 'olga_devops',
                'tags': ['git', 'docker', 'linux'],
            },
            {
                'title': 'Асинхронный Python: asyncio',
                'cat': 'python',
                'content': '<h2>asyncio</h2><p>Библиотека для написания конкурентного кода с async/await.</p>',
                'author': 'alex_dev',
                'tags': ['python', 'fastapi'],
            },
            {
                'title': 'TypeScript: продвинутые типы',
                'cat': 'frontend',
                'content': '<h2>Продвинутые типы</h2><p>Generic типы позволяют создавать переиспользуемые компоненты.</p>',
                'author': 'maria_coder',
                'tags': ['typescript', 'javascript', 'react'],
            },
        ]

        created_posts = []
        for i, pdata in enumerate(posts_list):
            post = Post.objects.create(
                title=pdata['title'],
                content=pdata['content'],
                cat=categories[pdata['cat'].lower()],
                author=users[pdata['author']],
                is_published=True,
                time_create=now - timedelta(hours=i),
                views=random.randint(50, 5000),
            )
            post.tags.set([tags[t] for t in pdata['tags']])
            created_posts.append(post)

        self.stdout.write(f'  Создано {len(created_posts)} постов')

        # Комментарии
        all_posts = {p.slug: p for p in Post.objects.all()}
        comments_data = [
            ('vvedenie-v-django-rest-framework', 'maria_coder', 'Отличная статья! Очень помогла разобраться с DRF.'),
            ('vvedenie-v-django-rest-framework', 'dmitry_front', 'А можно пример с аутентификацией через JWT?'),
            ('react-hooks-polnoe-rukovodstvo', 'alex_dev', 'Лучшее руководство по хукам, спасибо!'),
            ('react-hooks-polnoe-rukovodstvo', 'ivan_admin', 'Добавьте ещё про useReducer, пожалуйста.'),
            ('docker-dlya-nachinayushchih', 'ivan_admin', 'Отлично объяснены базовые концепции.'),
            ('docker-dlya-nachinayushchih', 'dmitry_front', 'После этой статьи разобрался с Docker. Спасибо!'),
            ('optimizaciya-postgresql-zaprosov', 'alex_dev', 'Полезная инфа про индексы, не знал про GIN.'),
        ]
        for slug, author_username, content in comments_data:
            if slug in all_posts:
                Comment.objects.create(
                    post=all_posts[slug],
                    author=users[author_username],
                    content=content,
                    created_at=now - timedelta(minutes=random.randint(10, 500)),
                )

        self.stdout.write(f'  Создано {len(comments_data)} комментариев')
        self.stdout.write(self.style.SUCCESS('Тестовые данные успешно добавлены!'))
