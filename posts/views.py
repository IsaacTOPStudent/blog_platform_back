from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import NotFound
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Post
from .serializers import PostSerializer, PostUpdateSerializer, PostDetailSerializer
from .permissions import user_can_read_post, user_can_edit_post, get_readable_posts_query
from .paginations import PostPagination


class PostListCreateView(generics.ListCreateAPIView):
    """
    GET -> posts list
    POST -> create a post 
    """

    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = PostPagination

    @extend_schema(
        operation_id='list_posts',
        description='Get list of posts that the user has permission to read. Returns empty list if no accessible posts.',
        responses={
            200: OpenApiResponse(
                response=PostSerializer(many=True),
                description="List of posts with pagination"
            ),
        },
        tags=['Posts']
    )
    def get(self, request, *args, **kwargs):
        """List posts with permission filtering"""
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        operation_id='create_post',
        description='Create a new blog post with configurable read and edit permissions',
        request=PostSerializer,
        responses={
            201: OpenApiResponse(
                response=PostSerializer,
                description="Post created successfully"
            ),
            400: OpenApiResponse(description="Invalid data"),
            401: OpenApiResponse(description="Authentication required"),
        },
        tags=['Posts']
    )
    def post(self, request, *args, **kwargs):
        """Create a new post"""
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        #automatically sets the author as the authenticated user
        serializer.save(author=self.request.user)

    def get_queryset(self):
        """Filter posts based on user permissions - returns empty if no accessible posts"""

        user = self.request.user

        query = get_readable_posts_query(user)

        return Post.objects.filter(query).order_by('-created_at')
    
class PostUpdateView(generics.UpdateAPIView):
    """
    PUT/PATCH -> update post content, title, and permissions
    Editing follows the permissions set on the post before the edit attempt
    """
    queryset = Post.objects.all()
    serializer_class = PostUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        operation_id='update_post',
        description='Update post content, title, and permissions. Editing follows the permissions set on the post before the edit attempt.',
        request=PostUpdateSerializer,
        responses={
            200: OpenApiResponse(
                response=PostUpdateSerializer,
                description="Post updated successfully"
            ),
            400: OpenApiResponse(description="Invalid data"),
            403: OpenApiResponse(description="No permission to edit this post"),
            404: OpenApiResponse(description="Post not found"),
        },
        tags=['Posts']
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        operation_id='partial_update_post',
        description='Partially update post content, title, and/or permissions.',
        request=PostUpdateSerializer,
        responses={
            200: OpenApiResponse(
                response=PostUpdateSerializer,
                description="Post updated successfully"
            ),
            400: OpenApiResponse(description="Invalid data"),
            403: OpenApiResponse(description="No permission to edit this post"),
            404: OpenApiResponse(description="Post not found"),
        },
        tags=['Posts']
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def get_object(self):
        post = super().get_object()
        user = self.request.user

        if not user_can_edit_post(user, post):
            raise PermissionDenied('You do not have permission to edit this post')
        
        return post
    
class PostDetailView(generics.RetrieveAPIView):

    """
    GET -> get specific post details (returns 404 if user doesn't have read access)
    """
    
    serializer_class = PostDetailSerializer
    queryset = Post.objects.all()

    @extend_schema(
        operation_id='retrieve_post',
        description='Get detailed view of a specific post. Returns 404 if user does not have read access.',
        responses={
            200: OpenApiResponse(
                response=PostDetailSerializer,
                description="Post details"
            ),
            404: OpenApiResponse(description="Post not found or no access"),
        },
        tags=['Posts']
    )
    def get(self, request, *args, **kwargs):
        """Get post details with permission check"""
        return super().get(request, *args, **kwargs)

    def get_object(self):
        post = super().get_object()
        user = self.request.user

        if not user_can_read_post(user, post):
            raise NotFound("Post Not Found")
        
        return post

class PostDeleteView(generics.DestroyAPIView):
    """
    DELETE -> permanently delete post and all associated data
    Only users with edit permission can delete
    """

    serializer_class = PostSerializer
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        operation_id='delete_post',
        description='Permanently delete a blog post. Only users with edit permission can delete. All associated likes and comments are also deleted.',
        responses={
            204: OpenApiResponse(description="Post deleted successfully"),
            403: OpenApiResponse(description="No permission to delete this post"),
            404: OpenApiResponse(description="Post not found"),
        },
        tags=['Posts']
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def perform_destroy(self, instance):
        user = self.request.user

        if not user_can_edit_post(user, instance):
            raise PermissionDenied("You don't have permission to delete this post")
        
        instance.delete()