"""Аналитика чтения статей и дашборд автора.

Модуль намеренно не зависит от DRF: его используют и API, и SSR-страница.
Одна запись PostView = один читатель (сессия) за день на конкретный пост.
Повторные события в тот же день обновляют глубину прокрутки и время чтения,
поэтому счётчики не раздуваются при перезагрузке страницы.
"""
from __future__ import annotations

from datetime import timedelta
from urllib.parse import urlparse

from django.db.models import Avg, Count, Q
from django.utils import timezone

from main.models import Post, PostView, Subscription

SOURCE_LABELS = {
    PostView.Source.DIRECT: 'Прямой заход',
    PostView.Source.INTERNAL: 'Внутри ФлакХаба',
    PostView.Source.SEARCH: 'Поиск',
    PostView.Source.SOCIAL: 'Соцсети',
    PostView.Source.HABR: 'Хабр',
    PostView.Source.EXTERNAL: 'Другие сайты',
}

SEARCH_HOSTS = (
    'google.', 'yandex.', 'bing.', 'duckduckgo.', 'yahoo.', 'baidu.',
    'mail.ru', 'go.mail.ru', 'rambler.', 'brave.', 'ecosia.', 'startpage.',
    'perplexity.ai', 'chatgpt.com', 'chat.openai.com',
)

SOCIAL_HOSTS = (
    't.me', 'telegram.', 'vk.com', 'vk.ru', 'ok.ru', 'twitter.com', 'x.com',
    'facebook.', 'instagram.', 'reddit.', 'linkedin.', 'youtube.', 'youtu.be',
    'dzen.ru', 'zen.yandex.', 'pikabu.ru', 'tiktok.com', 'discord.',
)

HABR_HOSTS = ('habr.com', 'habr.ru', 'habrastorage.org')

INTERNAL_HOSTS = ('flachub.ru', 'www.flachub.ru', 'localhost', '127.0.0.1')


def _host(value: str) -> str:
    if not value:
        return ''
    try:
        parsed = urlparse(value if '://' in value else f'https://{value}')
        return (parsed.hostname or '').lower().lstrip('.')
    except ValueError:
        return ''


def _matches(host: str, patterns: tuple[str, ...]) -> bool:
    return any(host == p or host.endswith(f'.{p}') or (p.endswith('.') and p in host) for p in patterns)


def classify_source(referrer: str = '', explicit: str = '', site_host: str = '') -> tuple[str, str]:
    """Вернуть (source, referrer_host) по Referer и подсказке с клиента."""
    host = _host(referrer)
    own_host = _host(site_host)
    internal = set(INTERNAL_HOSTS)
    if own_host:
        internal.add(own_host)

    valid = {choice for choice, _ in PostView.Source.choices}
    if explicit in valid and explicit != PostView.Source.DIRECT:
        if explicit == PostView.Source.HABR and not host:
            return explicit, ''
        if explicit != PostView.Source.HABR:
            return explicit, host

    if not host:
        return PostView.Source.DIRECT, ''
    if host in internal:
        return PostView.Source.INTERNAL, host
    if _matches(host, HABR_HOSTS):
        return PostView.Source.HABR, host
    if _matches(host, SEARCH_HOSTS):
        return PostView.Source.SEARCH, host
    if _matches(host, SOCIAL_HOSTS):
        return PostView.Source.SOCIAL, host
    return PostView.Source.EXTERNAL, host


def _clamp(value, low: int, high: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return low
    return max(low, min(high, number))


def record_post_read(post: Post, request, data: dict) -> PostView:
    """Создать или обновить событие чтения за сегодняшний день."""
    session = getattr(request, 'session', None)
    if session is not None and not session.session_key:
        session.create()
    session_key = (session.session_key if session is not None else '') or ''
    session_key = session_key[:64]

    user = request.user if getattr(request, 'user', None) and request.user.is_authenticated else None
    referrer = (data.get('referrer') or request.META.get('HTTP_REFERER') or '')[:1000]
    source, referrer_host = classify_source(
        referrer=referrer,
        explicit=str(data.get('source') or ''),
        site_host=request.get_host(),
    )

    scroll_depth = _clamp(data.get('scroll_depth', 0), 0, 100)
    read_seconds = _clamp(data.get('read_seconds', 0), 0, 24 * 60 * 60)
    is_read_complete = bool(data.get('is_read_complete'))

    view, created = PostView.objects.get_or_create(
        post=post,
        session_key=session_key,
        view_date=timezone.localdate(),
        defaults={
            'user': user,
            'source': source,
            'referrer_host': referrer_host,
            'scroll_depth': scroll_depth,
            'read_seconds': read_seconds,
            'is_read_complete': is_read_complete,
        },
    )
    if not created:
        view.user = view.user or user
        view.scroll_depth = max(view.scroll_depth, scroll_depth)
        view.read_seconds = max(view.read_seconds, read_seconds)
        view.is_read_complete = view.is_read_complete or is_read_complete
        if not view.referrer_host and referrer_host:
            view.source = source
            view.referrer_host = referrer_host
        view.save(update_fields=[
            'user', 'scroll_depth', 'read_seconds', 'is_read_complete',
            'source', 'referrer_host', 'updated_at',
        ])
    return view


def _percent(part: int, total: int) -> float:
    if not total:
        return 0.0
    return round(part * 100 / total, 1)


def build_author_dashboard(user, days: int = 30) -> dict:
    """Собрать статистику автора за период.

    Возвращает готовый к JSON словарь: KPI, график по дням, источники и
    таблицу статей. Никаких запросов на фронтенде — только рендер.
    """
    days = _clamp(days, 1, 365)
    today = timezone.localdate()
    start_date = today - timedelta(days=days - 1)

    posts = Post.objects.filter(author=user)
    published = posts.filter(is_published=Post.Status.PUBLISHED)
    views = PostView.objects.filter(post__author=user, view_date__gte=start_date)

    totals = views.aggregate(
        views_count=Count('id'),
        readers_count=Count('session_key', distinct=True),
        completed_count=Count('id', filter=Q(is_read_complete=True)),
        avg_seconds=Avg('read_seconds'),
        total_seconds=Count('read_seconds', filter=Q(read_seconds__gt=0)),
    )
    views_count = totals['views_count'] or 0
    completed_count = totals['completed_count'] or 0

    # Заполняем пропущенные дни нулями, чтобы график не «прыгал».
    by_day = {
        row['view_date']: row
        for row in views.values('view_date').annotate(
            views=Count('id'),
            completed=Count('id', filter=Q(is_read_complete=True)),
            readers=Count('session_key', distinct=True),
        )
    }
    daily = []
    for offset in range(days):
        day = start_date + timedelta(days=offset)
        row = by_day.get(day, {})
        daily.append({
            'date': day.isoformat(),
            'label': day.strftime('%d.%m'),
            'views': row.get('views', 0),
            'completed': row.get('completed', 0),
            'readers': row.get('readers', 0),
        })

    sources = []
    for row in views.values('source').annotate(count=Count('id')).order_by('-count'):
        source = row['source'] or PostView.Source.DIRECT
        sources.append({
            'source': source,
            'label': SOURCE_LABELS.get(source, source),
            'count': row['count'],
            'percent': _percent(row['count'], views_count),
        })

    top_posts = []
    for post in posts.annotate(
        period_views=Count('view_events', filter=Q(view_events__view_date__gte=start_date)),
        period_completed=Count(
            'view_events',
            filter=Q(view_events__view_date__gte=start_date, view_events__is_read_complete=True),
        ),
        period_avg_seconds=Avg(
            'view_events__read_seconds',
            filter=Q(view_events__view_date__gte=start_date),
        ),
    ).order_by('-period_views', '-views')[:10]:
        top_posts.append({
            'id': post.id,
            'title': post.title,
            'slug': post.slug,
            'post_type': post.post_type,
            'is_published': post.is_published,
            'views_total': post.views,
            'views': post.period_views,
            'completed': post.period_completed,
            'completion_rate': _percent(post.period_completed, post.period_views),
            'avg_read_seconds': round(post.period_avg_seconds or 0),
        })

    subscribers_total = Subscription.objects.filter(author=user).count()
    subscribers_new = Subscription.objects.filter(
        author=user,
        created_at__date__gte=start_date,
    ).count() if _subscription_has_created_at() else 0

    return {
        'period_days': days,
        'date_from': start_date.isoformat(),
        'date_to': today.isoformat(),
        'kpi': {
            'views': views_count,
            'readers': totals['readers_count'] or 0,
            'completed': completed_count,
            'completion_rate': _percent(completed_count, views_count),
            'avg_read_seconds': round(totals['avg_seconds'] or 0),
            'subscribers_total': subscribers_total,
            'subscribers_new': subscribers_new,
            'posts_total': posts.count(),
            'posts_published': published.count(),
        },
        'daily': daily,
        'sources': sources,
        'top_posts': top_posts,
    }


def _subscription_has_created_at() -> bool:
    """Subscription создавалась без timestamp в старых миграциях."""
    return any(field.name == 'created_at' for field in Subscription._meta.get_fields())
