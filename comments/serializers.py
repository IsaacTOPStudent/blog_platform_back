from rest_framework import serializers
from .models import Comment, Post

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.email')
    post = serializers.ReadOnlyField(source='post.title')
    content = serializers.CharField(allow_blank=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'content', 'created_at']
        read_only_fields = ['user', 'post', 'created_at']

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("Comment cannot be empty.")
        if len(value) > 2500:
            raise serializers.ValidationError("Comment cannot exceed 2500 characters")
        return value
        