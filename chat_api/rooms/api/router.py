from django.urls import path
from rooms.api.views import RegisterView, RoomApiView, RoomParticipateApiView, getRooms
urlpatterns = [
    # Crear y registrar en una sala
    path('rooms/register/', RegisterView.as_view(), name='register_room'),
    path('rooms/<int:room_id>/', RoomApiView.as_view(), name='room'),
    path('rooms/<int:room_id>/participate/', RoomParticipateApiView.as_view(), name='room_participate'),
    path('rooms/', getRooms.as_view(), name='rooms'),
]
