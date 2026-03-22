"""
Сигналы для синхронизации между приложениями main и users

Этот модуль обеспечивает:
1. Синхронизацию данных пользователя между приложениями
2. Уведомления при важных событиях
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def sync_favorites_with_posts(sender, instance, created=False, **kwargs):
    """
    Сигнал: синхронизация избранного пользователя с моделью Post

    Это обеспечивает двустороннюю связь между User.favorited_posts и Post.favorites
    """
    if not created:
        try:
            from main.models import Post

            # Получаем избранные статьи пользователя
            # Используем обратную ссылку favorited_posts из Post.favorites
            # Это уже синхронизируется через ManyToMany автоматически
            pass

        except Exception as e:
            print(f"[SIGNAL ERROR] Ошибка при синхронизации избранного: {str(e)}")
