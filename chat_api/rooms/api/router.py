from django.urls import path
from rooms.api.views import RoomApiViewId, RoomApiView, RoomFollowApiView, getRoomsFollow,getRoomById, getRooms
urlpatterns = [
    # Crear y registrar en una sala
    path('rooms/user/', RoomApiView.as_view(), name='register_room'),
    path('rooms/user/<int:room_id>/', RoomApiViewId.as_view(), name='room'),
    path('rooms/follow/<int:room_id>/', RoomFollowApiView.as_view(), name='rooms_follow'),
    path('rooms/follow/', getRoomsFollow.as_view(), name='rooms_follow'),
    path('rooms/<int:room_id>/', getRoomById.as_view(), name='get_room_by_id'),
    path('rooms/', getRooms.as_view(), name='get_room'),
]