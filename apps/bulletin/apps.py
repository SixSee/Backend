from django.apps import AppConfig


class BulletinConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.bulletin'

    def ready(self):
        from . import signals  # noqa