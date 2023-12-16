from rest_framework import serializers
from rooms.models import Room
from users.api.serializers import UserSerializerUsername

class RegisterRoomSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Room
        fields = ['name', 'description', 'image', 'is_active', 'user_id']

class RoomSerializer(serializers.ModelSerializer):
    followers = UserSerializerUsername(many=True)
    
    class Meta:
        model = Room
        fields = ['id', 'name', 'description', 'image', 'is_active', 'user_id', 'followers', 'created_at', 'updated_at', 'user_count']
