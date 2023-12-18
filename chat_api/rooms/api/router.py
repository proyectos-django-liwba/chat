from django.urls import path
from rooms.api.views import RoomViewSet, RoomGetViewSet, LeaveRoomAPIView, getRoomsParticipe


from rest_framework.routers import DefaultRouter


router_room = DefaultRouter()
router_room.register(prefix='rooms/user',viewset=RoomViewSet, basename='rooms')
router_room.register(prefix='rooms',viewset=RoomGetViewSet, basename='rooms')
