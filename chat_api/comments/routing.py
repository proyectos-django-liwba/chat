from django.urls import re_path

from comments.consumers import ChatConsumer

comments_websocket_urlpatterns= [

        re_path(
            r"ws/comments/(?P<room_id>\w+)/$", ChatConsumer.as_asgi(),
    ),
    
]