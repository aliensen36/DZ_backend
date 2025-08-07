from django.apps import AppConfig


class ResidentAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'resident_app'
    verbose_name = 'Резиденты'


    def ready(self):
        import resident_app.signals