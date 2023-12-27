from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from notification.models import Notification
from .serializers import NotificationSerializer
from rooms.models import Room
from users.models import User
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
class NotificationListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk, format=None):  # Cambia room_id a pk
        room = get_object_or_404(Room, id=pk)  # Usa pk como el ID de la habitación

        notifications = Notification.objects.filter(room=room)
        serializer = NotificationSerializer(notifications, many=True)

        return Response(serializer.data)

    def delete(self, request, pk, format=None):
        user_id = request.user.id  # El ID del usuario se obtiene directamente desde la solicitud debido a IsAuthenticated
        notification = get_object_or_404(Notification, id=pk)

        # Verificar si el usuario está vinculado a la notificación
        if notification.users.filter(id=user_id).exists():
            # Desvincular al usuario de la notificación
            notification.users.remove(user_id)

            # Verificar si no hay más usuarios vinculados a la notificación
            if not notification.users.exists():
                # No hay más usuarios, eliminar la notificación
                notification.delete()

            return Response({"message": "Usuario desvinculado correctamente."},
                            status=status.HTTP_200_OK)
        else:
            # El usuario no estaba vinculado a la notificación
            return Response({"error": "El usuario no está vinculado a la notificación."},
                            status=status.HTTP_400_BAD_REQUEST)


