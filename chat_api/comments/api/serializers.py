from rest_framework import serializers
from comments.models import Comment
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        content = serializers.JSONField(required=True)
        model = Comment
        fields = ['id', 'user_id', 'room_id', 'content', 'created_at', 'updated_at']
