from rest_framework import serializers
from comments.models import Comment
from users.api.serializers import UserSerializerUsername
class CommentSerializer(serializers.ModelSerializer):
    # Agrega un campo para serializar la información completa del usuario
    user_info = UserSerializerUsername(source='user', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user_id', 'room_id', 'content', 'created_at', 'updated_at', 'user_info']

        
class CommentSerializerList(serializers.ModelSerializer):
    user = UserSerializerUsername(source='user_id', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'room_id', 'user', 'content', 'created_at', 'updated_at']
        
    