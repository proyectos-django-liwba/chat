from rest_framework import serializers
from rooms.models import Room

class registerRoomSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Room
        fields = ['name','description','is_active','user']
        
        
class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id','name','description','is_active','user', 'users', 'created_at', 'updated_at']
