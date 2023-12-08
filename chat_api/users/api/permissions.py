from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Verificar si la solicitud es para editar o eliminar un objeto
        if request.method in ['PUT','PATCH', 'DELETE']:
            # Obtener el usuario autenticado
            user = request.user
            
            # Obtener el usuario que se va a actualizar desde los parámetros de la URL
            user_id = view.kwargs.get('pk')
            
            # Si es el dueño la cuenta, permitir la acción
            if user_id == user.id:
                return True
        # Si la solicitud no es para editar o eliminar, permitir la acción
        return False
