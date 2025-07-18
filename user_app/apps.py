from django.apps import AppConfig


class UserAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user_app'
    verbose_name = 'Пользователи'

    def ready(self):
        import user_app.signals
