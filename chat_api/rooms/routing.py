from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(
        r"ws/chat/(?P<room_id>\w+)/$",
        consumers.chatConsumer.as_asgi(),
    ),
    
    re_path(
        r"ws/user_count/(?P<room_id>\w+)/$",
        consumers.UserCountConsumer.as_asgi(),
    ),

]