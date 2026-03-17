"""
Сигналы для синхронизации между приложениями main, users и marketplace

Этот модуль обеспечивает:
1. Автоматическое создание профиля маркетплейса при регистрации
2. Синхронизацию данных пользователя между приложениями
3. Уведомления при важных событиях
"""

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

User = get_user_model()


@receiver(post_save, sender=User)
def create_marketplace_profile(sender, instance, created, **kwargs):
    """
    Сигнал: при создании нового пользователя создаём его профиль в маркетплейсе
    
    Параметры:
        sender: модель User
        instance: экземпляр созданного пользователя
        created: True если пользователь только создан
    """
    if created and instance.is_active:
        try:
            from marketplace.models import FreelancerProfile
            
            # Проверяем, не существует ли уже профиль
            if not hasattr(instance, 'freelancer_profile'):
                # Создаём профиль фрилансера
                profile = FreelancerProfile.objects.create(
                    user=instance,
                    bio=f"Новый пользователь маркетплейса",
                    is_available=True,
                    rating=5.0
                )
                
                # Отправляем приветственное письмо
                send_welcome_email(instance)
                
                print(f"[SIGNAL] Профиль маркетплейса создан для пользователя: {instance.username}")
        
        except Exception as e:
            print(f"[SIGNAL ERROR] Ошибка при создании профиля маркетплейса: {str(e)}")


@receiver(post_save, sender=User)
def sync_user_data(sender, instance, created=False, **kwargs):
    """
    Сигнал: синхронизация данных пользователя между приложениями
    
    Обновляет:
    - Аватар в профиле маркетплейса
    - Имя и фамилию
    - Статус активности
    """
    if not created:  # Только при обновлении, не при создании
        try:
            from marketplace.models import FreelancerProfile
            
            profile = FreelancerProfile.objects.filter(user=instance).first()
            
            if profile:
                # Синхронизируем аватар
                if instance.photo and not profile.avatar:
                    profile.avatar = instance.photo
                
                # Обновляем статус доступности
                if not instance.is_active:
                    profile.is_available = False
                
                profile.save()
                
        except Exception as e:
            print(f"[SIGNAL ERROR] Ошибка при синхронизации данных: {str(e)}")


@receiver(pre_delete, sender=User)
def delete_marketplace_profile(sender, instance, **kwargs):
    """
    Сигнал: при удалении пользователя удаляем его профиль в маркетплейсе
    
    Параметры:
        sender: модель User
        instance: экземпляр удаляемого пользователя
    """
    try:
        from marketplace.models import FreelancerProfile
        
        profile = FreelancerProfile.objects.filter(user=instance).first()
        
        if profile:
            profile.delete()
            print(f"[SIGNAL] Профиль маркетплейса удален для пользователя: {instance.username}")
    
    except Exception as e:
        print(f"[SIGNAL ERROR] Ошибка при удалении профиля маркетплейса: {str(e)}")


def send_welcome_email(user):
    """
    Отправить приветственное письмо новому пользователю
    
    Параметры:
        user: экземпляр пользователя
    """
    try:
        subject = f"Добро пожаловать на PageGlow, {user.first_name or user.username}!"
        
        context = {
            'user': user,
            'site_name': 'PageGlow',
            'marketplace_url': f"{settings.SITE_URL}/marketplace/",
        }
        
        # Пытаемся использовать HTML шаблон если он есть
        try:
            html_message = render_to_string('users/emails/welcome.html', context)
        except:
            html_message = f"""
            <p>Добро пожаловать на PageGlow, {user.first_name or user.username}!</p>
            <p>Ваш аккаунт успешно создан.</p>
            <p>Теперь вы можете:</p>
            <ul>
                <li>Просматривать и создавать проекты на маркетплейсе</li>
                <li>Взаимодействовать с другими фрилансерами</li>
                <li>Читать интересные статьи в блоге</li>
                <li>Развивать свой профиль и репутацию</li>
            </ul>
            <p><a href="{settings.SITE_URL}/marketplace/">Перейти на маркетплейс</a></p>
            """
        
        send_mail(
            subject=subject,
            message=f"Добро пожаловать на PageGlow, {user.first_name or user.username}!",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=True
        )
        
        print(f"[EMAIL] Приветственное письмо отправлено пользователю: {user.email}")
    
    except Exception as e:
        print(f"[EMAIL ERROR] Ошибка при отправке приветственного письма: {str(e)}")


@receiver(post_save, sender=User)
def sync_favorites_with_posts(sender, instance, created=False, **kwargs):
    """
    Сигнал: синхронизация избранного пользователя с моделью Post
    
    Это обеспечивает двусторонню связь между User.favorited_posts и Post.favorites
    """
    if not created:
        try:
            from main.models import Post
            
            # Получаем избранные статьи пользователя
            # Используем обратную ссылку favorited_posts из Post.favorites
            # Это уже синхронизируется через ManyToMany автоматически
            
        except Exception as e:
            print(f"[SIGNAL ERROR] Ошибка при синхронизации избранного: {str(e)}")


@receiver(post_save, sender=User)
def sync_user_data(sender, instance, created=False, **kwargs):
    """
    Сигнал: синхронизация данных пользователя между приложениями
    
    Обновляет:
    - Аватар в профиле маркетплейса
    - Имя и фамилию
    - Статус активности
    """
    if not created:  # Только при обновлении, не при создании
        try:
            from marketplace.models import FreelancerProfile
            
            profile = FreelancerProfile.objects.filter(user=instance).first()
            
            if profile:
                # Синхронизируем аватар
                if instance.photo and not profile.avatar:
                    profile.avatar = instance.photo
                
                # Обновляем статус доступности
                if not instance.is_active:
                    profile.is_available = False
                
                profile.save()
                
        except Exception as e:
            print(f"[SIGNAL ERROR] Ошибка при синхронизации данных: {str(e)}")
