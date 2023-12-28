from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from notification.models import Notification
from .serializers import NotificationSerializer
from rooms.models import Room
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth.models import User
from .permissions import IsFollowerOfRoom 
class NotificationListAPIView(APIView):
    permission_classes = [IsFollowerOfRoom]
    
    def get(self, request, format=None):
        user = request.user

        # Obtén todas las notificaciones para el usuario actual
        notifications = Notification.objects.filter(users=user)
        
        serializer = NotificationSerializer(notifications, many=True)
        return Response({"Notifications": serializer.data})



class NotificationDeleteApiView(APIView):
    def delete(self, request, pk, format=None):
        permission_classes = [IsAuthenticated]
        user_id = request.user.id
        notification = get_object_or_404(Notification, id=pk)

        # Verificar si el usuario está vinculado a la notificación
        if notification.users.filter(id=user_id).exists():
            # Desvincular al usuario de la notificación
            notification.users.remove(user_id)

            # Verificar si no hay más usuarios vinculados a la notificación
            if not notification.users.exists():
                # No hay más usuarios, eliminar la notificación
                notification.delete()

            return Response({"message": "Notificación eliminada correctamente."},
                            status=status.HTTP_200_OK)
        else:
            # El usuario no estaba vinculado a la notificación
            return Response({"error": "El usuario no está vinculado a la notificación."},
                            status=status.HTTP_400_BAD_REQUEST)


def create_and_save_notification(description, room, users, type, user,action):
    user_id = user.id
    notification = Notification(description=description, type=type, room=room, user_id=user_id)
    notification.save()
    notification.users.set(users)
    
    channel_layer = get_channel_layer()
    group_name = "notification_group"
    event = {
        "type": "recibir",
        "Notification": NotificationSerializer(notification).data,
        "action": action,

    }
    async_to_sync(channel_layer.group_send)(group_name, event)