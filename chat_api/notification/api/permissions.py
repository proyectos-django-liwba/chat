from rest_framework.permissions import BasePermission

class IsFollowerOfRoom(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Verifica si el usuario actual es seguidor de la sala asociada al objeto
        return request.user in obj.room.followers.all()