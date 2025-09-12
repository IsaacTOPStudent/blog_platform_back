from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied, ValidationError
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import Comment
from .patinationsComments import CommentPagination
from .serializers import CommentSerializer
from likes.utils import get_post_or_404_for_user

class CommentCreateView(generics.CreateAPIView):
    """
    Create a new comment on a blog post.
    Requires authentication and view access to the post.
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        operation_id='create_comment',
        description='Create a new comment on a blog post. Requires authentication and view access to the post.',
        request=CommentSerializer,
        responses={
            201: OpenApiResponse(
                response=CommentSerializer,
                description="Comment created successfully"
            ),
            400: OpenApiResponse(description="Invalid data"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="You must log in to comment"),
            404: OpenApiResponse(description="Post not found or no access"),
        },
        tags=['Comments']
    )
    def post(self, request, *args, **kwargs):
        """Create a comment on a post"""
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Validate comment attempt and then create it
        """
        post_id = self.kwargs.get('post_id')
        user = self.request.user 

        post = get_post_or_404_for_user(user, post_id)

        if not user.is_authenticated:
            raise PermissionDenied('You must log in to comment')
        
        serializer.save(user=user, post=post)

class CommentListView(generics.ListAPIView):
    """
    List comments for a specific blog post.
    Users can view all comments on any post for which they have view access.
    Supports filtering by user_id.
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = CommentPagination

    @extend_schema(
        operation_id='list_post_comments',
        description='Get all comments for a specific post. Users can view comments on any post they have view access to.',
        parameters=[
            OpenApiParameter(
                name='user_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filter comments by user ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=CommentSerializer(many=True),
                description="List of comments with pagination (max 10 per page)"
            ),
            400: OpenApiResponse(description="Invalid user_id parameter"),
            404: OpenApiResponse(description="Post not found or no access"),
        },
        tags=['Comments']
    )
    def get(self, request, *args, **kwargs):
        """Get comments for a post with optional user filtering"""
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        user = self.request.user

        post = get_post_or_404_for_user(user, post_id)

        queryset = Comment.objects.filter(post=post)

        user_id = self.request.query_params.get('user_id')
        if user_id:
            if not user_id.isdigit():
                raise ValidationError({'user_id': 'Must be a valid integer'})
            queryset = queryset.filter(user__id=user_id)
        return queryset.order_by('-created_at')

class CommentDeleteView(generics.DestroyAPIView):
    """
    Delete a comment.
    Only the comment author or superuser can delete a comment.
    Requires view access to the post.
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        operation_id='delete_comment',
        description='Delete a comment. Only the comment author or superuser can delete. Must have view access to the post.',
        responses={
            204: OpenApiResponse(description="Comment deleted successfully"),
            403: OpenApiResponse(description="Only author or admin can delete this comment"),
            404: OpenApiResponse(description="Comment not found or no access to post"),
        },
        tags=['Comments']
    )
    def delete(self, request, *args, **kwargs):
        """Delete a comment"""
        return super().delete(request, *args, **kwargs)
    
    def get_object(self):
        """
        Get comment and verify permissions.
        AC: Users can delete a comment that they have previously posted
        AC: Must have view access to the post
        """
        # Get the comment
        comment = super().get_object()
        user = self.request.user
        
        # AC: Must have view access to the post
        # This will raise 404 if user doesn't have view access to the post
        get_post_or_404_for_user(user, comment.post.id)
        
        return comment

    def get_queryset(self):
        return Comment.objects.all()
    
    def perform_destroy(self, instance):
         user = self.request.user
         if instance.user != user and not user.is_superuser:
             raise PermissionDenied('Only author or admin can delete this comment.')
         instance.delete()
