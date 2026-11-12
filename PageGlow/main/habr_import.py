"""Импорт статьи с Хабра по URL.

Пользователь вставляет ссылку вида https://habr.com/ru/articles/123456/
и получает готовый черновик: заголовок, очищенный HTML, теги и обложку.
Импорт ничего не публикует — только заполняет редактор.

Картинки скачиваются в MEDIA, чтобы статья не зависела от хотлинков и
не ломалась, если Хабр переедет. Скачиваем с ограничением по размеру и
только с разрешённых доменов (защита от SSRF).
"""
from __future__ import annotations

import hashlib
import mimetypes
import os
import re
from urllib.parse import urljoin, urlparse

import bleach
import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.files.storage import default_storage

USER_AGENT = (
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/124.0 Safari/537.36 FlachubImporter/1.0'
)
REQUEST_TIMEOUT = 15
MAX_IMAGE_BYTES = 8 * 1024 * 1024
MAX_IMAGES = 12

ARTICLE_HOSTS = ('habr.com', 'www.habr.com', 'habr.ru', 'www.habr.ru')
IMAGE_HOSTS = ('habrastorage.org', 'habr.com', 'habr.ru')

ALLOWED_TAGS = set(bleach.sanitizer.ALLOWED_TAGS) | {
    'p', 'div', 'span', 'br', 'hr', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'blockquote', 'pre', 'code', 'figure', 'figcaption',
    'img', 'table', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td',
    'strong', 'b', 'em', 'i', 'u', 's', 'del', 'ins', 'sub', 'sup',
    'dl', 'dt', 'dd', 'details', 'summary', 'mark', 'small',
}
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'rel', 'target'],
    'img': ['src', 'alt', 'title', 'width', 'height', 'loading'],
    'code': ['class'],
    'pre': ['class'],
    'span': ['class'],
    'div': ['class'],
    'figure': ['class'],
    'th': ['colspan', 'rowspan', 'scope'],
    'td': ['colspan', 'rowspan'],
    'details': ['open'],
}
ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']


class HabrImportError(Exception):
    """Ошибка импорта с человекочитаемым текстом для API."""


def _host_allowed(host: str, allowed: tuple[str, ...]) -> bool:
    host = (host or '').lower()
    return any(host == item or host.endswith(f'.{item}') for item in allowed)


def _validate_article_url(url: str) -> str:
    url = (url or '').strip()
    if not url:
        raise HabrImportError('Укажите ссылку на статью Хабра.')
    if not re.match(r'^https?://', url, re.I):
        url = f'https://{url}'
    parsed = urlparse(url)
    if not _host_allowed(parsed.hostname or '', ARTICLE_HOSTS):
        raise HabrImportError('Поддерживаются только ссылки на habr.com.')
    if not re.search(r'/(articles|post)/\d+/?', parsed.path):
        raise HabrImportError('Это не похоже на статью Хабра. Нужна ссылка вида habr.com/ru/articles/123456/.')
    return url


def _fetch(
    url: str,
    *,
    binary: bool = False,
    allowed_hosts: tuple[str, ...] = ARTICLE_HOSTS,
) -> requests.Response:
    """GET с ручной проверкой редиректов, чтобы не уйти на внутренний хост."""
    current = url
    for _ in range(4):
        response = requests.get(
            current,
            headers={'User-Agent': USER_AGENT, 'Accept-Language': 'ru,en;q=0.8'},
            timeout=REQUEST_TIMEOUT,
            stream=binary,
            allow_redirects=False,
        )
        if response.status_code in (301, 302, 303, 307, 308):
            location = response.headers.get('Location')
            if not location:
                response.raise_for_status()
            next_url = urljoin(current, location)
            parsed = urlparse(next_url)
            if (
                parsed.scheme not in ('http', 'https')
                or not _host_allowed(parsed.hostname or '', allowed_hosts)
            ):
                raise requests.RequestException('redirect to a disallowed host')
            response.close()
            current = next_url
            continue
        response.raise_for_status()
        return response
    raise requests.RequestException('too many redirects')


def _image_extension(content_type: str, url: str) -> str:
    content_type = (content_type or '').split(';')[0].strip().lower()
    ext = mimetypes.guess_extension(content_type) if content_type else None
    if ext in ('.jpe', '.jpeg'):
        ext = '.jpg'
    if not ext:
        ext = os.path.splitext(urlparse(url).path)[1].lower()
    if ext not in ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.avif'):
        ext = '.jpg'
    return ext


def _download_image(url: str) -> str:
    """Скачать картинку в MEDIA и вернуть локальный URL. При ошибке — исходный."""
    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https') or not _host_allowed(parsed.hostname or '', IMAGE_HOSTS):
        return url

    digest = hashlib.sha1(url.encode('utf-8')).hexdigest()[:20]
    try:
        response = _fetch(url, binary=True, allowed_hosts=IMAGE_HOSTS)
        content_type = response.headers.get('Content-Type', '')
        if not content_type.startswith('image/'):
            return url
        chunks = []
        size = 0
        for chunk in response.iter_content(64 * 1024):
            size += len(chunk)
            if size > MAX_IMAGE_BYTES:
                return url
            chunks.append(chunk)
        payload = b''.join(chunks)
        if not payload:
            return url

        ext = _image_extension(content_type, url)
        name = f'imports/habr/{digest}{ext}'
        if not default_storage.exists(name):
            default_storage.save(name, _BytesFile(payload))
        return f'{settings.MEDIA_URL}{name}'
    except Exception:
        return url


class _BytesFile:
    """Минимальный файловый адаптер для default_storage.save."""

    def __init__(self, payload: bytes):
        from io import BytesIO
        self._buffer = BytesIO(payload)

    def read(self, *args, **kwargs):
        return self._buffer.read(*args, **kwargs)

    def seek(self, *args, **kwargs):
        return self._buffer.seek(*args, **kwargs)

    def tell(self):
        return self._buffer.tell()


def _clean_body(body, base_url: str) -> str:
    soup = BeautifulSoup(str(body), 'html.parser')

    for tag in soup.select('script, style, noscript, iframe, form, button'):
        tag.decompose()

    downloaded = 0
    for img in soup.find_all('img'):
        src = img.get('src') or img.get('data-src') or ''
        if not src:
            img.decompose()
            continue
        src = urljoin(base_url, src)
        if downloaded < MAX_IMAGES:
            img['src'] = _download_image(src)
            downloaded += 1
        else:
            img['src'] = src
        img['loading'] = 'lazy'
        for attr in ('srcset', 'data-src', 'data-srcset', 'width', 'height'):
            img.attrs.pop(attr, None)

    for link in soup.find_all('a'):
        href = link.get('href') or ''
        if href and not href.startswith(('#', 'mailto:', 'tel:')):
            link['href'] = urljoin(base_url, href)
            link['rel'] = 'noopener noreferrer nofollow'

    cleaned = bleach.clean(
        str(soup),
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )
    return cleaned.strip()


def _extract_tags(soup: BeautifulSoup, title: str) -> list[str]:
    tags = []
    meta = soup.select_one('meta[name="keywords"]')
    if meta and meta.get('content'):
        tags = [item.strip() for item in meta['content'].split(',')]
    if not tags:
        for link in soup.select('a[href*="/ru/tags/"], a[href*="/tags/"]'):
            text = link.get_text(' ', strip=True)
            if text:
                tags.append(text)
    result = []
    for tag in tags:
        tag = re.sub(r'\s+', ' ', tag).strip(' #')
        if tag and tag.lower() != title.lower() and tag not in result:
            result.append(tag[:50])
        if len(result) >= 10:
            break
    return result


def import_habr_article(url: str) -> dict:
    """Разобрать статью Хабра и вернуть черновик для редактора."""
    url = _validate_article_url(url)
    try:
        response = _fetch(url)
    except requests.RequestException as exc:
        raise HabrImportError('Не удалось открыть статью. Проверьте ссылку и попробуйте ещё раз.') from exc

    response.encoding = response.apparent_encoding or 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    title_tag = soup.select_one('h1.tm-title') or soup.select_one('h1')
    title = title_tag.get_text(' ', strip=True) if title_tag else ''
    if not title:
        raise HabrImportError('Не удалось найти заголовок статьи. Возможно, Хабр изменил разметку.')

    body = soup.select_one('div.article-formatted-body') or soup.select_one('article')
    if not body:
        raise HabrImportError('Не удалось найти текст статьи. Возможно, Хабр изменил разметку.')

    content = _clean_body(body, url)
    if len(BeautifulSoup(content, 'html.parser').get_text(strip=True)) < 80:
        raise HabrImportError('Статья выглядит пустой — импортировать нечего.')

    cover = ''
    og_image = soup.select_one('meta[property="og:image"]')
    if og_image and og_image.get('content'):
        cover = _download_image(urljoin(url, og_image['content']))

    author_tag = soup.select_one('a.tm-user-info__username')
    description_tag = soup.select_one('meta[name="description"]')

    return {
        'title': title[:255],
        'content': content,
        'tags': _extract_tags(soup, title),
        'cover_url': cover,
        'source_url': url,
        'source': 'habr',
        'author': author_tag.get_text(' ', strip=True) if author_tag else '',
        'description': (description_tag.get('content', '') if description_tag else '')[:300],
    }
