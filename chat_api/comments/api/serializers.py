from rest_framework import serializers
from comments.models import Comment
from users.api.serializers import UserSerializerUsername
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        content = serializers.JSONField(required=True)
        model = Comment
        fields = ['id', 'user_id', 'room_id', 'content', 'created_at', 'updated_at']
        
class CommentSerializerList(serializers.ModelSerializer):
    user = UserSerializerUsername(source='user_id', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'room_id', 'user', 'content', 'created_at', 'updated_at']