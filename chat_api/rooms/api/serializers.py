from rest_framework import serializers
from rooms.models import Room
from django.contrib.auth.models import User 
from rooms.models import Room
from users.api.serializers import UserSerializerUsername
class registerRoomSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Room
        fields = ['name','description','is_active','user']
        
        
class RoomSerializer(serializers.ModelSerializer):
    users = UserSerializerUsername(many=True)

    class Meta:
        model = Room
        fields = ['id', 'name', 'description', 'is_active', 'user', 'users', 'created_at', 'updated_at']
