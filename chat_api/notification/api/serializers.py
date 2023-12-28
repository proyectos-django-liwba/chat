from rest_framework import serializers
from notification.models import Notification
from users.api.serializers import UserSerializerUsername
from rooms.api.serializers import RoomInfoSerializer


class NotificationSerializer(serializers.ModelSerializer):
    room = RoomInfoSerializer() 
    user = UserSerializerUsername()
    class Meta:
        model = Notification
        fields = ['id', 'description', 'created_at', 'room','user', 'users', 'type']

