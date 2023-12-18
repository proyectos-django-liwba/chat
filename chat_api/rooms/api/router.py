from django.urls import path
from rooms.api.views import RegisterView, RoomApiView, RoomParticipateApiView, getRooms, LeaveRoomAPIView, getRoomsParticipe
urlpatterns = [
    # Crear y registrar en una sala
    path('rooms/register/', RegisterView.as_view(), name='register_room'),
    path('rooms/<int:room_id>/', RoomApiView.as_view(), name='room'),
    path('rooms/<int:room_id>/participate/', RoomParticipateApiView.as_view(), name='room_participate'),
    path('rooms/', getRooms.as_view(), name='rooms'),
    path('rooms/<int:room_id>/leave/', LeaveRoomAPIView.as_view(), name='leave_room'),
    path('rooms/participate/', getRoomsParticipe.as_view(), name='rooms_participate'),
]
