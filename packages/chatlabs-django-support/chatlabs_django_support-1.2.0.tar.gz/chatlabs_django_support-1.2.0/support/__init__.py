def get_asgi_application():
    import django.core.asgi
    from channels.auth import AuthMiddlewareStack
    from channels.routing import ProtocolTypeRouter, URLRouter

    from .routing import ws_urlpatterns

    return ProtocolTypeRouter(
        {
            'http': django.core.asgi.get_asgi_application(),
            'websocket': AuthMiddlewareStack(URLRouter(ws_urlpatterns)),
        }
    )


__all__ = [
    'get_asgi_application',
]

__version__ = '1.2.0'
