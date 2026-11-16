import logging
import os
import json

from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views import View
from django.core.files.storage import FileSystemStorage

from PageGlow import settings
from main.models import Subscription
from users.reputation_utils import award_reputation, undo_reputation

logger = logging.getLogger(__name__)


def health_check(request):
    try:
        from django.core.cache import cache
        cache.set('health_check', 'ok', 10)
        cache.get('health_check')
        return JsonResponse({'status': 'healthy', 'database': 'ok', 'cache': 'ok'})
    except Exception as e:
        logger.error(f'Health check failed: {str(e)}')
        return JsonResponse({'status': 'unhealthy', 'error': str(e)}, status=503)


def robots_txt(request):
    return render(request, 'robots.txt', content_type='text/plain')


def page_not_found(request, exception):
    return render(request, '404.html', status=404)


def server_error(request):
    return render(request, '500.html', status=500)


def bad_gateway(request):
    return render(request, '502.html', status=502)


def service_unavailable(request):
    return render(request, '503.html', status=503)


def permission_denied(request, exception):
    return render(request, '403.html', status=403)


@method_decorator(login_required, name='dispatch')
class CKEditorUploadView(View):
    def post(self, request):
        try:
            file = request.FILES.get('upload') or request.FILES.get('file')
            if not file:
                return JsonResponse({'error': {'message': 'Файл не найден'}}, status=400)

            if file.size > 100 * 1024 * 1024:
                return JsonResponse({'error': {'message': 'Файл слишком большой (макс. 100 МБ)'}}, status=400)

            allowed_types = [
                'image/jpeg', 'image/png', 'image/gif', 'image/webp',
                'image/x-icon', 'image/vnd.microsoft.icon'
            ]
            if file.content_type not in allowed_types:
                return JsonResponse({'error': {'message': f'Недопустимый тип файла: {file.content_type}'}}, status=400)

            upload_path = os.path.join(settings.MEDIA_ROOT, 'ckeditor', 'uploads')
            os.makedirs(upload_path, exist_ok=True)

            import uuid
            ext = os.path.splitext(os.path.basename(file.name))[1].lstrip('.').lower()
            if ext not in {'jpg', 'jpeg', 'png', 'gif', 'webp', 'ico'}:
                ext = 'jpg'
            unique_filename = f'{uuid.uuid4().hex}.{ext}'

            fs = FileSystemStorage(location=upload_path)
            fs.save(unique_filename, file)
            file_url = f"{settings.MEDIA_URL}ckeditor/uploads/{unique_filename}"

            return JsonResponse({'url': file_url, 'uploaded': True})
        except Exception as e:
            logger.error(f"Upload error: {str(e)}", exc_info=True)
            return JsonResponse({'error': {'message': f'Ошибка загрузки: {str(e)}'}}, status=500)


@login_required
def toggle_subscribe(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    author_id = request.POST.get('author_id')
    if not author_id:
        return JsonResponse({'error': 'author_id is required'}, status=400)

    from django.contrib.auth import get_user_model
    User = get_user_model()

    try:
        target_user = User.objects.get(id=author_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

    if target_user == request.user:
        return JsonResponse({'error': 'Cannot subscribe to yourself'}, status=400)

    subscription = Subscription.objects.filter(
        subscriber=request.user,
        author=target_user
    ).first()

    if subscription:
        subscription.delete()
        undo_reputation(target_user, 'subscription_received')
        subscribed = False
    else:
        Subscription.objects.create(
            subscriber=request.user,
            author=target_user
        )
        award_reputation(target_user, 'subscription_received')
        subscribed = True

    return JsonResponse({
        'success': True,
        'subscribed': subscribed,
        'subscribers_count': target_user.subscribers.count(),
    })


def post_ssr(request, slug):
    """SSR-страница статьи: HTML, мета-теги и начальные данные для React."""
    from django.conf import settings as django_settings
    from django.http import Http404
    from django.shortcuts import get_object_or_404
    from django.utils.html import strip_tags
    from main.models import Post
    from main.ssr import absolute_media_url, get_vite_assets
    from mobile_api.serializers import PostDetailSerializer

    post = get_object_or_404(
        Post.objects.select_related('cat', 'author', 'reviewer').prefetch_related('tags', 'comments'),
        slug=slug,
    )

    if not post.is_published:
        # Черновик доступен только автору и персоналу. Отдаём обычную SPA-оболочку,
        # чтобы React показал предпросмотр через API.
        is_owner = request.user.is_authenticated and post.author_id == request.user.id
        if not (is_owner or request.user.is_staff):
            raise Http404
        return render(request, 'index.html')

    initial_post = PostDetailSerializer(post, context={'request': request}).data
    canonical = request.build_absolute_uri(post.get_absolute_url())
    site_url = request.build_absolute_uri('/')
    description = ' '.join(strip_tags(post.content or '').split())
    if len(description) > 180:
        description = description[:177].rsplit(' ', 1)[0] + '…'
    if not description:
        description = f'Статья «{post.title}» на ФлакХабе.'

    cover = absolute_media_url(request, post.photo.url) if post.photo else request.build_absolute_uri('/static/images/og-default.jpg')
    logo = request.build_absolute_uri('/static/images/og-default.jpg')
    author_name = post.author.username if post.author else 'ФлакХаб'
    tags = [tag.tag for tag in post.tags.all()]

    json_ld = {
        '@context': 'https://schema.org',
        '@type': 'Article',
        'headline': post.title,
        'description': description,
        'image': [cover],
        'datePublished': post.time_create.isoformat(),
        'dateModified': post.time_update.isoformat(),
        'author': {'@type': 'Person', 'name': author_name},
        'publisher': {
            '@type': 'Organization',
            'name': 'ФлакХаб',
            'url': site_url,
            'logo': {'@type': 'ImageObject', 'url': logo},
        },
        'mainEntityOfPage': {'@type': 'WebPage', '@id': canonical},
        'keywords': ', '.join(tags),
        'inLanguage': 'ru',
    }

    context = {
        'post': post,
        'initial_post': initial_post,
        'canonical': canonical,
        'meta_title': f'{post.title} — ФлакХаб',
        'meta_description': description,
        'meta_image': cover,
        'meta_keywords': ', '.join(tags),
        'meta_author': author_name,
        'json_ld': json.dumps(json_ld, ensure_ascii=False),
        'vite_js': get_vite_assets()['js'],
        'vite_css': get_vite_assets()['css'],
        'site_name': 'ФлакХаб',
        'site_domain': getattr(django_settings, 'SITE_DOMAIN', 'flachub.ru'),
    }
    return render(request, 'post_ssr.html', context)
