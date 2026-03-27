"""
Темплейс-теги для отображения системы репутации
"""
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def get_user_level(user):
    """
    Получить текущий уровень пользователя
    
    Usage: {% get_user_level user as level %}
    """
    if not user or not user.is_authenticated:
        return None
    return user.current_level


@register.simple_tag
def get_user_reputation(user):
    """
    Получить репутацию пользователя
    
    Usage: {% get_user_reputation user as reputation %}
    """
    if not user or not user.is_authenticated:
        return 0
    return user.reputation


@register.simple_tag
def get_level_progress(user):
    """
    Получить прогресс до следующего уровня (0-100%)
    
    Usage: {% get_level_progress user as progress %}
    """
    if not user or not user.is_authenticated:
        return 0
    return user.level_progress


@register.inclusion_tag('users/templatetags/user_level_badge.html', takes_context=True)
def user_level_badge(context, user):
    """
    Отобразить бейдж уровня пользователя
    
    Usage: {% user_level_badge user %}
    """
    if not user or not user.is_authenticated:
        level = None
        progress = 0
        reputation = 0
    else:
        level = user.current_level
        progress = user.level_progress
        reputation = user.reputation
    
    return {
        'level': level,
        'progress': progress,
        'reputation': reputation,
        'user': user,
    }


@register.inclusion_tag('users/templatetags/reputation_summary.html', takes_context=True)
def reputation_summary(context, user):
    """
    Отобразить сводку репутации пользователя с прогресс-баром
    
    Usage: {% reputation_summary user %}
    """
    if not user or not user.is_authenticated:
        level = None
        next_level = None
        progress = 0
        reputation = 0
    else:
        level = user.current_level
        next_level = user.next_level
        progress = user.level_progress
        reputation = user.reputation
    
    return {
        'level': level,
        'next_level': next_level,
        'progress': progress,
        'reputation': reputation,
        'user': user,
    }


@register.simple_tag
def render_level_icon(level):
    """
    Отобразить иконку уровня с цветом
    
    Usage: {% render_level_icon level %}
    """
    if not level:
        return mark_safe('<span class="level-icon" title="Без уровня">🌱</span>')
    
    html = f'''
        <span class="level-icon" 
              style="color: {level.color};" 
              title="{level.name}">
            {level.icon}
        </span>
    '''
    return mark_safe(html)


@register.simple_tag
def can_user_perform_action(user, action_type):
    """
    Проверить, может ли пользователь выполнить действие
    
    Usage: {% can_user_perform_action user 'create_tags' as can_create %}
    """
    if not user or not user.is_authenticated:
        return False
    return user.can_perform_action(action_type)


@register.inclusion_tag('users/templatetags/next_level_info.html', takes_context=True)
def next_level_info(context, user):
    """
    Отобразить информацию о следующем уровне
    
    Usage: {% next_level_info user %}
    """
    if not user or not user.is_authenticated:
        return {
            'next_level': None,
            'progress': 0,
            'reputation_needed': 0,
        }
    
    next_level = user.next_level
    reputation_needed = 0
    
    if next_level:
        reputation_needed = next_level.min_reputation - user.reputation
    
    return {
        'next_level': next_level,
        'progress': user.level_progress,
        'reputation_needed': max(0, reputation_needed),
        'user': user,
    }


@register.simple_tag
def get_reputation_change_class(amount):
    """
    Получить CSS класс для изменения репутации
    
    Usage: {% get_reputation_change_class amount %}
    """
    if amount > 0:
        return 'reputation-positive'
    elif amount < 0:
        return 'reputation-negative'
    else:
        return 'reputation-neutral'


@register.inclusion_tag('users/templatetags/top_users_reputation.html', takes_context=True)
def top_users_reputation(context, limit=10):
    """
    Отобразить топ пользователей по репутации
    
    Usage: {% top_users_reputation limit=10 %}
    """
    from users.models import User
    from django.db.models import Sum
    
    top_users = User.objects.annotate(
        total_reputation=Sum('reputation_logs__amount')
    ).order_by('-total_reputation')[:limit]
    
    # Добавляем уровни к пользователям
    for user in top_users:
        user._level = user.current_level
    
    return {
        'top_users': top_users,
        'limit': limit,
    }
