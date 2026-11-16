"""Серверный рендер статьи и чтение Vite-манифеста.

React-приложение остаётся SPA, но страница статьи получает готовый HTML:
поисковики и соцсети видят заголовок, текст, OG-теги и JSON-LD сразу,
а пользователь — контент до загрузки JS. После монтирования React
заменяет серверный shell и забирает данные из window.__INITIAL_POST__.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from django.conf import settings


def _asset_url(path: str) -> str:
    if path.startswith(('http://', 'https://', '/')):
        return path
    return f'/{path.lstrip("/")}'


def get_vite_assets() -> dict:
    """Вернуть JS/CSS entry-файлы сборки Vite.

    Основной источник — .vite/manifest.json. Если манифеста нет
    (старая сборка), разбираем build/index.html.
    """
    build_dir = Path(settings.FRONTEND_BUILD_DIR)
    manifest_path = build_dir / '.vite' / 'manifest.json'

    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
            entry = next(
                (item for item in manifest.values() if item.get('isEntry')),
                None,
            )
            if entry:
                js, css = [], []
                queue = [entry]
                seen = set()
                while queue:
                    item = queue.pop(0)
                    file = item.get('file')
                    if file and file.endswith('.js') and file not in js:
                        js.append(file)
                    for css_file in item.get('css', []) or []:
                        if css_file not in css:
                            css.append(css_file)
                    for imported in item.get('imports', []) or []:
                        if imported in seen:
                            continue
                        seen.add(imported)
                        if imported in manifest:
                            queue.append(manifest[imported])
                return {
                    'js': [_asset_url(item) for item in js],
                    'css': [_asset_url(item) for item in css],
                }
        except (OSError, ValueError, TypeError):
            pass

    index_path = build_dir / 'index.html'
    if index_path.exists():
        try:
            html = index_path.read_text(encoding='utf-8')
            js = re.findall(r'<script[^>]+src="([^"]+\.js)"', html)
            css = re.findall(r'<link[^>]+href="([^"]+\.css)"', html)
            return {
                'js': [_asset_url(item) for item in js],
                'css': [_asset_url(item) for item in css],
            }
        except OSError:
            pass

    return {'js': [], 'css': []}


def absolute_media_url(request, url: str) -> str:
    if not url:
        return ''
    if url.startswith(('http://', 'https://')):
        return url
    return request.build_absolute_uri(url)
