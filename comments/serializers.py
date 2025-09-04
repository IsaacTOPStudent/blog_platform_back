from rest_framework import serializers
from .models import Comment

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'content', 'created_at']
        read_only_fields = ['user', 'created_at']