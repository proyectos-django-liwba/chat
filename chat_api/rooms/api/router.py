from django.urls import path
from rooms.api.views import RoomViewSet, getRooms, LeaveRoomAPIView, getRoomsParticipe,getRoomById


from rest_framework.routers import DefaultRouter


router_room = DefaultRouter()
router_room.register(prefix='rooms/user',viewset=RoomViewSet, basename='categoria')
