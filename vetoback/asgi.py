
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vetoback.settings')
django.setup()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import bettingGame.routing
from django.core.asgi import get_asgi_application
from . import urls
application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            bettingGame.routing.websocket_urlpatterns
        )
    ),
})

