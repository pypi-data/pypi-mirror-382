from typing import TYPE_CHECKING

from django.conf import settings
from django.db import models

if TYPE_CHECKING:
    from django_stubs_ext.db.models.manager import RelatedManager


def get_telegram_user_model():
    """
    Возвращает модель пользователя Telegram, указанную в
    `settings.SUPPORT_TELEGRAM_USER_MODEL`.
    """
    from django.apps import apps

    return apps.get_model(
        settings.SUPPORT_TELEGRAM_USER_MODEL, require_ready=False
    )


class Ticket(models.Model):
    id = models.BigAutoField(
        verbose_name='ID',
        primary_key=True,
        unique=True,
    )
    created_at = models.DateTimeField(
        verbose_name='Создан в',
        auto_now_add=True,
    )
    user = models.ForeignKey(
        verbose_name='Пользователь',
        to=settings.SUPPORT_TELEGRAM_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tickets',
    )
    title = models.CharField(
        verbose_name='Заголовок',
        max_length=256,
    )
    support_manager = models.ForeignKey(
        verbose_name='Менеджер поддержки',
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='tickets',
        null=True,
        blank=True,
    )
    resolved = models.BooleanField(
        verbose_name='Решен',
        default=False,
    )
    viewed = models.BooleanField(
        verbose_name='Просмотрено',
        default=False,
    )

    if TYPE_CHECKING:
        messages: RelatedManager['Message']

    class Meta:
        verbose_name = 'Тикет'
        verbose_name_plural = 'Тикеты'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Message(models.Model):
    class Sender(models.TextChoices):
        USER = 'user', 'Пользователь'
        SUPPORT_MANAGER = 'supp', 'Менеджер поддержки'

    id = models.BigAutoField(
        verbose_name='ID',
        primary_key=True,
        unique=True,
    )
    created_at = models.DateTimeField(
        verbose_name='Создано в',
        auto_now_add=True,
    )
    ticket = models.ForeignKey(
        verbose_name='Тикет',
        to=Ticket,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    sender = models.CharField(
        verbose_name='Отправитель',
        max_length=4,
        choices=Sender.choices,
        default=Sender.USER,
    )
    text = models.CharField(
        verbose_name='Текст',
        max_length=4096,
    )

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        text = f'{self.text[:20]}...'
        sender = self.sender_instance
        if sender is None:
            return text
        return f'{sender}: {text}'

    @property
    def sender_instance(self):
        match self.sender:
            case self.Sender.USER:
                return self.ticket.user
            case self.Sender.SUPPORT_MANAGER:
                return self.ticket.support_manager
            case _:
                return None
