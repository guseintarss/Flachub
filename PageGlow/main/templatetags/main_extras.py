import markdown
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django.utils import timezone
from datetime import timedelta

register = template.Library()

@register.filter
@stringfilter
def render_markdown(value):
    md = markdown.Markdown(extensions=['fenced_code'])
    return mark_safe(md.convert(value))


@register.filter
def time_ago(value):
    """
    Отображает время публикации в формате "X секунд/минут/часов/дней/лет назад"
    """
    if not value:
        return ""
    
    # Если это наивное datetime, добавляем информацию о текущей временной зоне
    if value.tzinfo is None:
        value = timezone.make_aware(value)
    
    now = timezone.now()
    diff = now - value
    
    seconds = int(diff.total_seconds())
    
    if seconds < 60:
        return "только что" if seconds < 10 else f"{seconds} сек. назад"
    
    minutes = seconds // 60
    if minutes < 60:
        if minutes == 1:
            return "1 мин. назад"
        return f"{minutes} мин. назад"
    
    hours = minutes // 60
    if hours < 24:
        if hours == 1:
            return "1 час назад"
        return f"{hours} часов назад"
    
    days = hours // 24
    if days < 7:
        if days == 1:
            return "вчера"
        return f"{days} дней назад"
    
    weeks = days // 7
    if weeks < 4:
        if weeks == 1:
            return "1 неделю назад"
        return f"{weeks} недель назад"
    
    months = days // 30
    if months < 12:
        if months == 1:
            return "1 месяц назад"
        return f"{months} месяцев назад"
    
    years = days // 365
    if years == 1:
        return "1 год назад"
    return f"{years} лет назад"