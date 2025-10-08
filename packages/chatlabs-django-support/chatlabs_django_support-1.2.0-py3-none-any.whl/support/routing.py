from django.urls import path

from . import consumers

ws_urlpatterns = [
    path(
        'ws/support/manager/',
        consumers.ChatConsumer.as_asgi()
    ),
]
