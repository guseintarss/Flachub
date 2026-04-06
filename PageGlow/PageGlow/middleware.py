"""
SEO Middleware для ФлакХаб
Автоматически добавляет SEO-оптимизированные meta-теги и заголовки
"""
import re
from django.utils.deprecation import MiddlewareMixin


class SEOMiddleware(MiddlewareMixin):
    """Middleware для автоматической SEO-оптимизации"""

    def process_response(self, request, response):
        # Не обрабатываем AJAX запросы и статические файлы
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return response

        # Добавляем X-Robots-Tag для служебных страниц
        if any(request.path.startswith(prefix) for prefix in [
            '/admin/', '/api/', '/health/', '/__debug__/',
            '/bookmarks/', '/ajax/', '/feed/',
        ]):
            response['X-Robots-Tag'] = 'noindex, nofollow'

        # Добавляем Vary: Accept-Encoding для кэширования gzip
        if 'Content-Encoding' in response or response.get('Content-Type', '').startswith('text/'):
            response['Vary'] = 'Accept-Encoding'

        # Добавляем Content-Language для всех страниц
        if 'Content-Language' not in response:
            response['Content-Language'] = 'ru'

        return response


class MetaDescriptionMiddleware(MiddlewareMixin):
    """Middleware для автогенерации meta description из контента"""

    def process_view(self, request, view_func, view_args, view_kwargs):
        pass

    def process_template_response(self, request, response):
        # Работаем только с HTML ответами
        content_type = getattr(response, 'content_type', '')
        if 'text/html' not in content_type:
            return response

        if not hasattr(response, 'context_data') or response.context_data is None:
            return response

        context = response.context_data

        # Если meta_description уже задан — не трогаем
        if context.get('meta_description'):
            return response

        # Автогенерация meta description из контекста
        description = self._generate_description(context)
        if description:
            context['meta_description'] = description

        return response

    def _generate_description(self, context):
        """Генерирует SEO-friendly description из контекста"""
        # Для постов/статей
        post = context.get('post') or context.get('object')
        if post and hasattr(post, 'content'):
            text = re.sub(r'<[^>]+>', '', str(post.content))
            text = re.sub(r'\s+', ' ', text).strip()
            if len(text) > 160:
                # Находим границу слова на ~155 символах
                truncated = text[:155]
                last_space = truncated.rfind(' ')
                if last_space > 100:
                    truncated = truncated[:last_space]
                return truncated + '...'
            return text

        # Для страницы поиска
        q = context.get('q')
        if q:
            count = context.get('page_obj')
            results = f' найдено {count.paginator.count}' if count and count.paginator.count else ''
            return f'Результаты поиска по запросу "{q}"{results}. Найдите статьи, обсуждения и материалы по вашему запросу на ФлакХаб.'

        # Для категории
        category = context.get('category')
        if category:
            posts_count = getattr(category, 'posts_count', '')
            count_text = f' ({posts_count} статей)' if posts_count else ''
            return f'Статьи и материалы по теме "{category.name}"{count_text}. Публикации экспертов и разработчиков на ФлакХаб.'

        # Для тега
        tag = context.get('tag')
        if tag:
            return f'Все публикации с тегом "{tag.tag}". Статьи, обсуждения и материалы от IT-специалистов на ФлакХаб.'

        # Для профиля автора
        author = context.get('author')
        if author:
            bio = getattr(author, 'about_me', '')
            if bio:
                text = re.sub(r'<[^>]+>', '', str(bio))
                text = re.sub(r'\s+', ' ', text).strip()
                if len(text) > 160:
                    return text[:155] + '...'
                return f'Профиль автора {author.username} на ФлакХаб. {text}'
            return f'Профиль автора {author.username} на ФлакХаб. Все публикации, статьи и обсуждения.'

        # Для главной страницы
        if context.get('posts') is not None and not context.get('q'):
            return 'ФлакХаб — платформа для IT-специалистов. Читайте статьи по программированию, участвуйте в обсуждениях, делитесь знаниями и развивайтесь вместе с нами.'

        return None
