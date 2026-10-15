from django.apps import AppConfig


class CsplAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cspl_app'

    def ready(self):
        # Import signals to ensure they are registered
        import cspl_app.signals
