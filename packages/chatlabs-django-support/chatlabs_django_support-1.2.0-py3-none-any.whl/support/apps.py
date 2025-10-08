from django.apps import AppConfig
from django.db.models.signals import post_save


class SupportConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'support'
    verbose_name = 'Поддержка'

    def ready(self) -> None:
        from . import models, signals

        post_save.connect(signals.post_save_ticket, models.Ticket)
        post_save.connect(signals.post_save_message, models.Message)
