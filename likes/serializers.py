from rest_framework import serializers
from .models import Like

class LikeSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = Like
        fields = ['id', 'user', 'created_at']
        read_only_fields=['user', 'created_at']

class LikeActionSerializer(serializers.Serializer):
    """
    Serializer to document the input of the like action
    """
    pass