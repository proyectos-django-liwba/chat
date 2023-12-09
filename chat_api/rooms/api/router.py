from django.urls import path
from rooms.api.views import RegisterView, RoomApiView

urlpatterns = [
    # Crear y registrar en una sala
    path('rooms/register/', RegisterView.as_view(), name='register_room'),
    path('rooms/<int:room_id>/', RoomApiView.as_view(), name='room'),
]
