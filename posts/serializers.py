from rest_framework import serializers
from .models import Post
from .permissions import validate_permission_hierarchy_values

class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username') #only read

    class Meta:
        model = Post
        fields = ['id', 'author', 'title', 'content', 'excerpt', 'created_at', 'author_access', 'team_access', 'authenticated_access', 'public_access']

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)

        author_access = attrs.get('author_access', getattr(instance, 'author_access', 'write'))
        team_access = attrs.get('team_access', getattr(instance, 'team_access', 'none'))
        authenticated_access = attrs.get('authenticated_access', getattr(instance, 'authenticated_access', 'none'))
        public_access = attrs.get('public_access', getattr(instance, 'public_access', 'none'))

        errors = validate_permission_hierarchy_values(author_access, team_access, authenticated_access, public_access)

        if errors:
            raise serializers.ValidationError(errors)
        
        return attrs

class PostDetailSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'excerpt', 'created_at', 'update_at', 'author', 'author_access', 'team_access', 'authenticated_access', 'public_access']

class PostUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'content', 'author_access', 'team_access', 'authenticated_access', 'public_access']

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)

        author_access = attrs.get('author_access', getattr(instance, 'author_access', 'write'))
        team_access = attrs.get('team_access', getattr(instance, 'team_access', 'none'))
        authenticated_access = attrs.get('authenticated_access', getattr(instance, 'authenticated_access', 'none'))
        public_access = attrs.get('public_access', getattr(instance, 'public_access', 'none'))


        errors = validate_permission_hierarchy_values(author_access, team_access, authenticated_access, public_access)

        if errors:
            raise serializers.ValidationError(errors)
        
        return attrs