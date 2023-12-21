from django.urls import re_path

from . import consumers

rooms_websocket_urlpatterns = [
    re_path(
        r"ws/chat/(?P<room_id>\w+)/$",
        consumers.RoomConsumer.as_asgi(),
    ),
    
    re_path(
        r"ws/user_count/(?P<room_id>\w+)/$",
        consumers.UserCountConsumer.as_asgi(),
    ),
    
    re_path(
        r'ws/salas/$', consumers.SalaConsumer.as_asgi(),
    ),

]