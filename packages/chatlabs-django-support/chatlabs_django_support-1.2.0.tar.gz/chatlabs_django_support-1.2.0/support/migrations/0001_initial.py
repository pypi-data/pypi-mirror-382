import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ticket',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        primary_key=True,
                        serialize=False,
                        unique=True,
                        verbose_name='ID',
                    ),
                ),
                (
                    'created_at',
                    models.DateTimeField(
                        auto_now_add=True, verbose_name='Создан в'
                    ),
                ),
                (
                    'title',
                    models.CharField(max_length=256, verbose_name='Заголовок'),
                ),
                (
                    'resolved',
                    models.BooleanField(default=False, verbose_name='Решен'),
                ),
                (
                    'support_manager',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='tickets',
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='Менеджер поддержки',
                    ),
                ),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='tickets',
                        to=settings.SUPPORT_TELEGRAM_USER_MODEL,
                        verbose_name='Пользователь',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Тикет',
                'verbose_name_plural': 'Тикеты',
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        primary_key=True,
                        serialize=False,
                        unique=True,
                        verbose_name='ID',
                    ),
                ),
                (
                    'created_at',
                    models.DateTimeField(
                        auto_now_add=True, verbose_name='Создано в'
                    ),
                ),
                (
                    'sender',
                    models.CharField(
                        choices=[
                            ('user', 'Пользователь'),
                            ('supp', 'Менеджер поддержки'),
                        ],
                        default='user',
                        max_length=4,
                        verbose_name='Отправитель',
                    ),
                ),
                (
                    'text',
                    models.CharField(max_length=4096, verbose_name='Текст'),
                ),
                (
                    'viewed',
                    models.BooleanField(
                        default=False, verbose_name='Просмотрено'
                    ),
                ),
                (
                    'ticket',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='messages',
                        to='support.ticket',
                        verbose_name='Тикет',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Сообщение',
                'verbose_name_plural': 'Сообщения',
            },
        ),
    ]
