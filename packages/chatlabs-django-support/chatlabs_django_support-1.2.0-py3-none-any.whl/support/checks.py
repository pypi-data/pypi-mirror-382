from django.apps import apps
from django.conf import settings
from django.core.checks import Error, register


@register()
def check_telegram_user_model(app_configs, **kwargs):  # noqa: ARG001
    errors = []
    model_path = getattr(settings, 'SUPPORT_TELEGRAM_USER_MODEL', None)

    if not model_path:
        errors.append(
            Error(
                'SUPPORT_TELEGRAM_USER_MODEL не указан в settings.py',
                id='support.E001',
            )
        )
        return errors

    try:
        model = apps.get_model(model_path, require_ready=False)
    except LookupError:
        errors.append(
            Error(
                f"SUPPORT_TELEGRAM_USER_MODEL '{model_path}' не найден",
                id='support.E002',
            )
        )
        return errors

    if not hasattr(model, 'telegram_id'):
        errors.append(
            Error(
                f"SUPPORT_TELEGRAM_USER_MODEL '{model_path}' должен содержать "
                "поле 'telegram_id'",
                id='support.E003',
            )
        )

    return errors
