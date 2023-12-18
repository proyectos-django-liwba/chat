
from rest_framework.permissions import BasePermission
from rooms.models import Room
from rest_framework.response import Response
from rest_framework import status
class RoomPermission(BasePermission):
    def has_object_permission(self, request, view, obj):

        user = request.user

        room_owner = obj.user_id

        # Verificar si el usuario autenticado es el propietario de la sala o un administrador
        if user == room_owner or user.role == 'Admin':
            # Permitir editar y eliminar la sala
            return request.method in ['PUT', 'DELETE']

        # Verificar si el usuario es un participante
        if obj.followers.filter(id=user.id).exists():
            # Permitir salirse de la sala
            return request.method == 'PATCH'


        # Si el usuario no tiene permisos, devolver una respuesta personalizada
        error_message = "Usted no tiene permisos para realizar esta acción en esta sala."
        response_data = {"error": error_message}
        return Response(response_data, status=status.HTTP_403_FORBIDDEN)
