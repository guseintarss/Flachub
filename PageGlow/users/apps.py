from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'
    verbose_name = 'Пользователи'
    
    def ready(self):
        """Регистрируем сигналы при инициализации приложения"""
        import users.signals
