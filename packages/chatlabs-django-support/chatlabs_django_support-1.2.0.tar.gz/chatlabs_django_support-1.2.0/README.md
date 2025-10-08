# ChatLabs Django Support

## Зависимости

- Python 3.11+
- [Django](https://pypi.org/project/Django/) 5.0.1
- [Channels](https://pypi.org/project/channels/) >=4.2.0,<5.0.0
- [Daphne](https://pypi.org/project/daphne/) >=4.1.2,<5.0.0
- [Django REST framework](https://pypi.org/project/djangorestframework/) >=3.15.2,<4.0.0
- [Django-filter](https://pypi.org/project/django-filter/) >=24.3,<25.0

## Установка

Установите пакет через `pip`:
```bash
pip install chatlabs-django-support
```

...или через `Poetry`:
```bash
poetry add chatlabs-django-support
```

## Быстрый старт

1. Добавьте модель Telegram пользователя в любое ваше приложение:
    ```python
    # my_users/models.py

    class MyTelegramUser(models.Model):
        telegram_id = models.BigIntegerField(
            primary_key=True,
            unique=True,
        )
    ```

2. Добавьте `daphne`, `channels`, `support` и приложение с вашей моделью Telegram пользователя в `INSTALLED_APPS`:
    ```python
    # settings.py

    INSTALLED_APPS = [
        'daphne',
        'channels',
        ...,
        'my_users',
        'support',
    ]
    ```

3. Укажите модель Telegram пользователя в настройках:
    ```python
    # settings.py

    SUPPORT_TELEGRAM_USER_MODEL = 'my_users.MyTelegramUser'
    ```

4. Также необходимо настроить слои для `channels`:
    ```python
    # settings.py

    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    }
    ```

5. Настройте ASGI-приложение:
    ```python
    # asgi.py

    import os

    from support import get_asgi_application

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'example.settings')

    application = get_asgi_application()
    ```

    ```python
    # settings.py

    ASGI_APPLICATION = 'example.asgi.application'
    ```

6. Обновите `urls.py`:
    ```python
    from django.urls import path, include

    urlpatterns = [
        ...
        path('support/', include('support.urls')),
    ]
    ```

7. Создайте и выполните миграции:
    ```bash
    python manage.py makemigrations
    ```

    ```bash
    python manage.py migrate
    ```

### API

---

GET "/support/tickets/"

Получить список тикетов

**Query params**:
- `user_id` (number) - ID Пользователя (создателя тикета)
- `resolved` (bool) - `true` - тикет решен, `false` - тикет не решен
- `manager` (number) - ID менеджера, на которого назначены тикеты
- `manager__isnull` (bool) - `true` - менеджер не назначен, `false` - менеджер назначен

**Response**:
```json
[
    {
        "id": 2,
        "user": {
            "telegram_id": 123
        },
        "support_manager": null,
        "created_at": "2025-01-31T12:24:25.716425Z",
        "title": "I've founded some bug",
        "resolved": false
    }
]
```

---

GET "/support/tickets/`ticket_id`/"

Получить тикет

**Response**:
```json
{
    "id": 1,
    "user": {
        "telegram_id": 123
    },
    "support_manager": {
        "id": 1,
        "first_name": "",
        "last_name": ""
    } || null,
    "created_at": "2025-01-22T12:11:40.273325Z",
    "title": "I've founded some bug",
    "resolved": true
}
```

---

GET "/support/tickets/`ticket_id`/messages/"

Получить список сообщений в тикете

**Response**:
```json
[
    {
        "id": 3,
        "created_at": "2025-01-31T12:18:03.929086Z",
        "sender": "user" || "supp",
        "text": "some text of message",
        "viewed": false,
        "ticket": 1
    }
]
```

---

### WebSocket API - Отправляемые сообщения

---

Принять тикет в работу:
```json
{
    "type": "ticket.assign",
    "ticket_id": 16 // ID тикета
}
```

---

Отправить сообщение:
```json
{
    "type": "ticket.message.new",
    "ticket_id": 16, // ID тикета
    "text": "The is some text" // текст сообщения
}
```

---

### WebSocket API - Получаемые сообщения

---

Создан новый тикет:
```json
{
    "type": "ticket.created",
    "ticket": {
        "id": 21, // ID тикета
        "user": { // Информация о пользователе
            "telegram_id": 4 // telegram_id пользователя
        },
        "support_manager": null, // назначенный менеджер
        "created_at": "2024-12-29T16:10:38.620768Z", // дата создания
        "title": "have a prob" // заголовок тикета
    }
}
```

---

Тикет назначен:
```json
{
    "type": "ticket.assigned",
    "id": 16, // ID тикета
    "support_manager": 1, // ID менеджера
}
```

---

Новое сообщение:
```json
{
    "type": "ticket.message.new",
    "message": {
        "id": 31, // ID сообщения
        "created_at": "2024-12-29T16:08:04.267002Z", // дата создания
        "sender": "supp", // отправитель, "user" - пользователь, "supp" - менеджер
        "text": "some_text", // текст сообщения
        "viewed": true, // сообщение просмотрено
        "ticket": 16 // ID тикета
    }
}
```

---
