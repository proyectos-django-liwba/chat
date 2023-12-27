from rest_framework import serializers
from rooms.models import Room
from users.api.serializers import UserSerializerUsername

class RegisterRoomSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Room
        fields = ['name', 'description', 'image', 'is_active', 'user_id']

class RoomSerializer(serializers.ModelSerializer):
    #followers = UserSerializerUsername(many=True)
    user = UserSerializerUsername(source='user_id')
    class Meta:
        
        model = Room
        fields = ['id', 'name', 'description', 'image',  'user', 'created_at',  'user_count', 'followers', 'updated_at']

class RoomPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name', 'description', 'image', 'user_count']
        
        
class RoomInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name']