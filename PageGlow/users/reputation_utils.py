"""
Утилиты системы репутации пользователей

Настройки начисления репутации за различные действия.
"""
from django.db import transaction, models
from django.utils import timezone
from datetime import timedelta

# ===== Конфигурация репутации =====

REPUTATION_SETTINGS = {
    # Публикация контента
    'post_created': 10,           # Создание поста
    'comment_created': 2,         # Создание комментария

    # Получение лайков
    'post_liked': 1,              # Лайк поста (автору)
    'comment_liked': 1,           # Лайк комментария (автору)

    # Социальные действия
    'subscription_received': 3,   # Подписка на автора
    'answer_accepted': 15,        # Лучший ответ в обсуждении

    # Нарушения
    'penalty_small': -5,          # Малое нарушение
    'penalty_medium': -15,        # Среднее нарушение
    'penalty_large': -50,         # Серьёзное нарушение
}

# Лимиты
DAILY_REPUTATION_LIMIT = 100  # Максимум репутации в день от одного пользователя


def get_reputation_value(reason):
    """
    Получить значение репутации для причины
    
    Args:
        reason: Строка причины (из UserReputationLog.ReasonType)
    
    Returns:
        int: Значение репутации
    """
    return REPUTATION_SETTINGS.get(reason, 0)


def check_daily_limit(giver_user, receiver_user, amount):
    """
    Проверка дневного лимита репутации
    
    Args:
        giver_user: Пользователь, который даёт репутацию
        receiver_user: Пользователь, который получает репутацию
        amount: Количество репутации
    
    Returns:
        bool: Можно ли начислить репутацию
    """
    today = timezone.now().date()
    
    # Сколько репутации этот пользователь уже дал сегодня другим
    given_today = giver_user.reputation_logs.filter(
        created_at__date=today,
        amount__gt=0
    ).aggregate(total=models.Sum('amount'))['total'] or 0
    
    # Проверяем лимит
    if given_today + amount > DAILY_REPUTATION_LIMIT:
        return False
    
    return True


@transaction.atomic
def award_reputation(user, reason, amount=None, post=None, comment=None, skip_limit=False):
    """
    Начислить репутацию пользователю

    Args:
        user: Пользователь, получающий репутацию
        reason: Причина (из UserReputationLog.ReasonType)
        amount: Количество (если None, берётся из настроек)
        post: Связанный пост
        comment: Связанный комментарий
        skip_limit: Пропустить проверку дневного лимита

    Returns:
        bool: Успешно ли начислена репутация
    """
    if amount is None:
        amount = get_reputation_value(reason)

    if amount == 0:
        return False

    # Проверка дневного лимита на получение репутации (для положительных значений)
    if amount > 0 and not skip_limit:
        today = timezone.now().date()
        received_today = user.reputation_logs.filter(
            created_at__date=today,
            amount__gt=0
        ).aggregate(total=models.Sum('amount'))['total'] or 0

        # Лимит на получение репутации в день (5x от базового)
        max_daily_receive = DAILY_REPUTATION_LIMIT * 5
        if received_today + amount > max_daily_receive:
            return False

    # Начисляем репутацию
    user.add_reputation(
        amount=amount,
        reason=reason,
        post=post,
        comment=comment
    )

    return True


def undo_reputation(user, reason, post=None, comment=None):
    """
    Отменить начисление репутации (например, при удалении лайка)

    Args:
        user: Пользователь, у которого отменяется репутация
        reason: Причина отмены
        post: Связанный пост
        comment: Связанный комментарий
    """
    amount = get_reputation_value(reason)
    if amount == 0:
        return

    # Отменяем, вычитая репутацию
    user.add_reputation(
        amount=-amount,
        reason=reason,
        post=post,
        comment=comment
    )


def get_top_users_by_reputation(limit=10):
    """
    Получить топ пользователей по репутации
    
    Args:
        limit: Количество пользователей
    
    Returns:
        QuerySet: Пользователи с аннотированной репутацией
    """
    from django.db.models import Sum
    from users.models import User
    
    return User.objects.annotate(
        total_reputation=models.Sum('reputation_logs__amount')
    ).order_by('-total_reputation')[:limit]


def apply_penalty(user, penalty_type, reason_text=''):
    """
    Применить штраф к пользователю
    
    Args:
        user: Пользователь
        penalty_type: Тип штрафа ('small', 'medium', 'large')
        reason_text: Текст причины
    """
    penalty_map = {
        'small': REPUTATION_SETTINGS['penalty_small'],
        'medium': REPUTATION_SETTINGS['penalty_medium'],
        'large': REPUTATION_SETTINGS['penalty_large'],
    }
    
    amount = penalty_map.get(penalty_type, REPUTATION_SETTINGS['penalty_small'])
    
    user.add_reputation(
        amount=amount,
        reason='penalty',
    )
    
    # Создаём уведомление
    from main.models import Notification
    Notification.objects.create(
        recipient=user,
        notification_type='achievement',
        message=f'Штраф репутации: {reason_text} ({amount})'
    )
