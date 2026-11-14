"""Импорт кода из GitHub в черновик разбора.

Поддерживаются ссылки на публичный репозиторий, отдельный файл и pull request.
Модуль ходит только на api.github.com, проверяет редиректы и ограничивает
размер и количество файлов, чтобы не превратить импорт в SSRF или способ
съесть память большим репозиторием.
"""
from __future__ import annotations

import base64
import html
import re
from urllib.parse import quote, urljoin, urlparse

import requests
from django.conf import settings

API_HOST = 'api.github.com'
GITHUB_HOSTS = ('github.com', 'www.github.com')
REQUEST_TIMEOUT = 20
MAX_FILES = 10
MAX_FILE_BYTES = 160 * 1024
MAX_TOTAL_BYTES = 600 * 1024
MAX_TREE_ENTRIES = 4000

USER_AGENT = 'FlachubGitHubImporter/1.0'

LANGUAGE_BY_EXTENSION = {
    'py': 'Python',
    'js': 'JavaScript',
    'jsx': 'JavaScript',
    'mjs': 'JavaScript',
    'cjs': 'JavaScript',
    'ts': 'TypeScript',
    'tsx': 'TypeScript',
    'go': 'Go',
    'rs': 'Rust',
    'java': 'Java',
    'kt': 'Kotlin',
    'kts': 'Kotlin',
    'swift': 'Swift',
    'cs': 'C#',
    'c': 'C++',
    'h': 'C++',
    'cc': 'C++',
    'cpp': 'C++',
    'hpp': 'C++',
    'php': 'PHP',
    'rb': 'Ruby',
    'sql': 'SQL',
    'html': 'HTML',
    'htm': 'HTML',
    'css': 'CSS',
    'scss': 'CSS',
    'dart': 'Dart',
    'sh': 'Bash',
    'bash': 'Bash',
    'yml': 'YAML',
    'yaml': 'YAML',
    'json': 'JSON',
    'md': 'Markdown',
}

SKIP_DIRECTORIES = {
    'node_modules', 'vendor', 'dist', 'build', 'coverage', 'target',
    '__pycache__', '.git', '.venv', 'venv', 'site-packages', 'migrations',
}
SKIP_FILE_MARKERS = (
    '.min.js', '.min.css', 'package-lock.json', 'yarn.lock',
    'pnpm-lock.yaml', 'poetry.lock', 'composer.lock',
)
NON_CODE_EXTENSIONS = {'md', 'json', 'yml', 'yaml'}


class GitHubImportError(Exception):
    """Ошибка импорта с человекочитаемым текстом для API."""


def _host_allowed(host: str, allowed: tuple[str, ...]) -> bool:
    host = (host or '').lower()
    return any(host == item or host.endswith(f'.{item}') for item in allowed)


def _github_headers() -> dict:
    headers = {
        'Accept': 'application/vnd.github+json',
        'User-Agent': USER_AGENT,
        'X-GitHub-Api-Version': '2022-11-28',
    }
    token = getattr(settings, 'GITHUB_TOKEN', '') or ''
    if token:
        headers['Authorization'] = f'Bearer {token}'
    return headers


def _fetch_json(path: str, params: dict | None = None) -> dict | list:
    """GET к GitHub API с ручной проверкой редиректов."""
    url = f'https://{API_HOST}{path}'
    current = url
    for _ in range(4):
        try:
            response = requests.get(
                current,
                headers=_github_headers(),
                params=params if current == url else None,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=False,
            )
        except requests.RequestException as exc:
            raise GitHubImportError('Не удалось связаться с GitHub. Попробуйте ещё раз.') from exc

        if response.status_code in (301, 302, 303, 307, 308):
            location = response.headers.get('Location')
            if not location:
                break
            next_url = urljoin(current, location)
            parsed = urlparse(next_url)
            if parsed.scheme != 'https' or not _host_allowed(parsed.hostname or '', (API_HOST,)):
                raise GitHubImportError('GitHub перенаправил запрос на недопустимый адрес.')
            current = next_url
            continue

        if response.status_code == 404:
            raise GitHubImportError('Репозиторий, файл или PR не найден. Проверьте, что он публичный.')
        if response.status_code in (401, 403, 429):
            raise GitHubImportError('GitHub временно ограничил запросы. Попробуйте позже.')
        if response.status_code >= 400:
            raise GitHubImportError(f'GitHub ответил ошибкой {response.status_code}.')
        try:
            return response.json()
        except ValueError as exc:
            raise GitHubImportError('GitHub вернул неожиданный ответ.') from exc

    raise GitHubImportError('Слишком много перенаправлений от GitHub.')


def _validate_url(url: str) -> tuple[str, str, str, str | None]:
    """Разобрать ссылку и вернуть owner, repo, kind и detail."""
    url = (url or '').strip()
    if not url:
        raise GitHubImportError('Укажите ссылку на GitHub.')
    if not re.match(r'^https?://', url, re.I):
        url = f'https://{url}'
    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https') or not _host_allowed(parsed.hostname or '', GITHUB_HOSTS):
        raise GitHubImportError('Поддерживаются только ссылки на github.com.')

    parts = [part for part in parsed.path.split('/') if part]
    if len(parts) < 2:
        raise GitHubImportError('Ссылка должна вести на репозиторий, файл или pull request.')
    owner, repo = parts[0], parts[1]
    if not re.match(r'^[\w.-]+$', owner) or not re.match(r'^[\w.-]+$', repo):
        raise GitHubImportError('Не удалось разобрать имя репозитория в ссылке.')

    if len(parts) >= 4 and parts[2] == 'pull' and parts[3].isdigit():
        return owner, repo, 'pr', parts[3]
    if len(parts) >= 5 and parts[2] == 'blob':
        ref = parts[3]
        path = '/'.join(parts[4:])
        return owner, repo, 'file', f'{ref}:{path}'
    if len(parts) >= 5 and parts[2] == 'tree':
        ref = parts[3]
        path = '/'.join(parts[4:])
        return owner, repo, 'tree', f'{ref}:{path}'
    return owner, repo, 'repo', None


def _language_for(path: str) -> str:
    extension = path.rsplit('.', 1)[-1].lower() if '.' in path else ''
    return LANGUAGE_BY_EXTENSION.get(extension, '')


def _is_code_path(path: str, size: int = 0) -> bool:
    if not path or path.endswith('/'):
        return False
    if size and size > MAX_FILE_BYTES:
        return False
    lower = path.lower()
    if any(marker in lower for marker in SKIP_FILE_MARKERS):
        return False
    if any(part in SKIP_DIRECTORIES for part in lower.split('/')):
        return False
    extension = lower.rsplit('.', 1)[-1] if '.' in lower else ''
    if extension in NON_CODE_EXTENSIONS:
        return False
    return bool(_language_for(path))


def _read_file(owner: str, repo: str, ref: str, path: str, remaining: int) -> dict | None:
    payload = _fetch_json(
        f'/repos/{quote(owner)}/{quote(repo)}/contents/{quote(path, safe="/")}',
        params={'ref': ref},
    )
    if not isinstance(payload, dict):
        return None
    if payload.get('type') != 'file' or payload.get('encoding') != 'base64':
        return None
    size = int(payload.get('size') or 0)
    if size > MAX_FILE_BYTES or size > remaining:
        return None
    try:
        content = base64.b64decode(payload.get('content') or '').decode('utf-8')
    except (ValueError, UnicodeDecodeError):
        return None
    if '\x00' in content:
        return None
    return {
        'path': payload.get('path') or path,
        'language': _language_for(payload.get('path') or path),
        'content': content,
        'size': size,
        'lines': len(content.splitlines()),
    }


def _repo_info(owner: str, repo: str) -> dict:
    payload = _fetch_json(f'/repos/{quote(owner)}/{quote(repo)}')
    if not isinstance(payload, dict):
        raise GitHubImportError('Не удалось прочитать данные репозитория.')
    return payload


def _files_from_repo(owner: str, repo: str, branch: str | None = None, prefix: str = '') -> list[dict]:
    info = _repo_info(owner, repo)
    ref = branch or info.get('default_branch') or 'main'
    tree = _fetch_json(
        f'/repos/{quote(owner)}/{quote(repo)}/git/trees/{quote(ref, safe="")}',
        params={'recursive': '1'},
    )
    if not isinstance(tree, dict):
        raise GitHubImportError('Не удалось прочитать файлы репозитория.')
    entries = [
        entry for entry in tree.get('tree', [])
        if entry.get('type') == 'blob'
        and _is_code_path(entry.get('path', ''), int(entry.get('size') or 0))
        and (not prefix or entry.get('path', '').startswith(prefix.rstrip('/') + '/'))
    ][:MAX_TREE_ENTRIES]
    entries.sort(key=lambda entry: (entry.get('path', '').count('/'), entry.get('size') or 0))

    files = []
    total = 0
    for entry in entries:
        if len(files) >= MAX_FILES:
            break
        file_data = _read_file(owner, repo, ref, entry['path'], MAX_TOTAL_BYTES - total)
        if not file_data:
            continue
        files.append(file_data)
        total += file_data['size']
        if total >= MAX_TOTAL_BYTES:
            break
    return files


def _files_from_pull(owner: str, repo: str, number: str) -> tuple[dict, list[dict]]:
    pull = _fetch_json(f'/repos/{quote(owner)}/{quote(repo)}/pulls/{quote(number)}')
    if not isinstance(pull, dict):
        raise GitHubImportError('Не удалось прочитать pull request.')
    files_payload = _fetch_json(
        f'/repos/{quote(owner)}/{quote(repo)}/pulls/{quote(number)}/files',
        params={'per_page': 100},
    )
    if not isinstance(files_payload, list):
        raise GitHubImportError('Не удалось прочитать файлы pull request.')

    ref = (pull.get('head') or {}).get('sha') or ''
    if not ref:
        raise GitHubImportError('У pull request нет доступной ветки.')

    files = []
    total = 0
    for item in files_payload:
        if len(files) >= MAX_FILES:
            break
        path = item.get('filename') or ''
        if item.get('status') == 'removed' or not _is_code_path(path, int(item.get('size') or 0)):
            continue
        file_data = _read_file(owner, repo, ref, path, MAX_TOTAL_BYTES - total)
        if not file_data:
            continue
        file_data['additions'] = int(item.get('additions') or 0)
        file_data['deletions'] = int(item.get('deletions') or 0)
        files.append(file_data)
        total += file_data['size']
        if total >= MAX_TOTAL_BYTES:
            break
    return pull, files


def _build_result(url: str, kind: str, title: str, description: str, files: list[dict], meta: dict | None = None) -> dict:
    if not files:
        raise GitHubImportError('В источнике не нашлось подходящих файлов с кодом.')
    first = files[0]
    description = (description or '').strip()
    file_items = ''.join(
        f'<li><code>{html.escape(item["path"])}</code> — {item["lines"]} строк</li>'
        for item in files
    )
    content = f'<h1>{html.escape(title)}</h1>'
    if description:
        content += f'<p>{html.escape(description[:2000])}</p>'
    content += f'<p>Файлы из GitHub:</p><ul>{file_items}</ul>'

    result = {
        'source': 'github',
        'kind': kind,
        'source_url': url,
        'title': title[:255],
        'description': description[:2000],
        'content': content,
        'files': files,
        'code_snippet': first['content'],
        'code_language': first['language'],
        'truncated': len(files) >= MAX_FILES,
    }
    if meta:
        result.update(meta)
    return result


def import_github_source(url: str) -> dict:
    """Разобрать ссылку GitHub и вернуть черновик разбора."""
    owner, repo, kind, detail = _validate_url(url)

    if kind == 'pr':
        pull, files = _files_from_pull(owner, repo, detail or '')
        title = pull.get('title') or f'{owner}/{repo} PR #{detail}'
        description = pull.get('body') or ''
        return _build_result(
            url, kind, title, description, files,
            {'pr_number': int(detail), 'repository': f'{owner}/{repo}'},
        )

    if kind == 'file':
        ref, path = (detail or '').split(':', 1)
        file_data = _read_file(owner, repo, ref, path, MAX_TOTAL_BYTES)
        if not file_data:
            raise GitHubImportError('Не удалось прочитать файл. Возможно, он слишком большой или не является текстом.')
        return _build_result(
            url, kind, f'{owner}/{repo}: {path}', '', [file_data],
            {'repository': f'{owner}/{repo}'},
        )

    if kind == 'tree':
        ref, path = (detail or '').split(':', 1)
        files = _files_from_repo(owner, repo, branch=ref, prefix=path)
        return _build_result(
            url, kind, f'{owner}/{repo}: {path}', '', files,
            {'repository': f'{owner}/{repo}'},
        )

    info = _repo_info(owner, repo)
    files = _files_from_repo(owner, repo)
    title = info.get('full_name') or f'{owner}/{repo}'
    return _build_result(
        url, kind, title, info.get('description') or '', files,
        {'repository': f'{owner}/{repo}'},
    )
