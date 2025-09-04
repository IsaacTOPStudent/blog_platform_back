from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username') #only read

    class Meta:
        model = Post
        fields = ['id', 'author', 'title', 'content', 'excerpt', 'created_at', 'read_permission', 'edit_permission']

class PostDetailSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'excerpt', 'created_at', 'update_at', 'read_permission', 'edit_permission', 'author']

class PostUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'content', 'read_permission', 'edit_permission']

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.read_permission = validated_data.get('read_permission', instance.read_permission)
        instance.edit_permission = validated_data.get('edit_permission', instance.edit_permission)
        instance.save()
        return instance