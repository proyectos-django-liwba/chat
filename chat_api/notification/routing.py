from django.urls import re_path

from notification.consumers import NotificationConsumer

notifications_websocket_urlpatterns= [

        re_path(
            r"ws/notifications/", NotificationConsumer.as_asgi(),
    ),
    
]