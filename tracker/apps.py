# tracker/apps.py
from django.apps import AppConfig


class TrackerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tracker'

    def ready(self):
        """
        Import signals when the app is ready.
        """
        # Implicitly connects signal handlers decorated with @receiver.
        from . import signals # noqa F401 - Tells linters not to complain about unused import
