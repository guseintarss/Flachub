import logging
import os
import json

from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views import View
from django.core.files.storage import FileSystemStorage

from PageGlow import settings

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
@method_decorator(csrf_exempt, name='dispatch')
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
                'image/x-icon', 'image/vnd.microsoft.icon', 'image/svg+xml'
            ]
            if file.content_type not in allowed_types:
                return JsonResponse({'error': {'message': f'Недопустимый тип файла: {file.content_type}'}}, status=400)

            upload_path = os.path.join(settings.MEDIA_ROOT, 'ckeditor', 'uploads')
            os.makedirs(upload_path, exist_ok=True)

            import uuid
            ext = file.name.split('.')[-1] if '.' in file.name else 'jpg'
            unique_filename = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex

            fs = FileSystemStorage(location=upload_path)
            fs.save(unique_filename, file)
            file_url = f"{settings.MEDIA_URL}ckeditor/uploads/{unique_filename}"

            return JsonResponse({'url': file_url, 'uploaded': True})
        except Exception as e:
            logger.error(f"Upload error: {str(e)}", exc_info=True)
            return JsonResponse({'error': {'message': f'Ошибка загрузки: {str(e)}'}}, status=500)
