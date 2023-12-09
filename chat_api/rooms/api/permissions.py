
from rest_framework.permissions import BasePermission
from rooms.models import Room

class RoomPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        
        user = request.user

        room_owner = obj.user

        # Verificar si el usuario autenticado es el propietario de la sala o un administrador
        if user == room_owner or user.role == 'Admin':
            # Permitir editar y eliminar la sala
            return request.method in ['PUT', 'DELETE']

        # Verificar si el usuario es un participante
        if obj.users.filter(id=user.id).exists():
            # Permitir salirse de la sala
            return request.method == 'PATCH'


        return False
