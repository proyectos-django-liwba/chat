import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from rooms.routing import rooms_websocket_urlpatterns
from comments.routing import comments_websocket_urlpatterns
django_asgi_app = get_asgi_application()



os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chat_api.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(
                rooms_websocket_urlpatterns
            )
        ),
    }
)