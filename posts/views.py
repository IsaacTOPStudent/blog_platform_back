from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import NotFound
from .models import Post
from .serializers import PostSerializer, PostUpdateSerializer, PostDetailSerializer
from .permissions import user_can_read_post, user_can_edit_post
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

    def perform_create(self, serializer):
        #automatically sets the author as the authenticated user
        serializer.save(author=self.request.user)

    def get_queryset(self):
        user = self.request.user

        #if the user is Not Authenticated - can only see public posts

        if user.is_authenticated and (user.is_superuser or user.role == 'admin'):
            return Post.objects.all()

        if not user.is_authenticated:
            return Post.objects.filter(read_permission='public')
        
        #if user is Authenticated

        return Post.objects.filter(
            read_permission='public'
        ) | Post.objects.filter(
            #Authenticated: any logged in user
            read_permission='authenticated'
        ) | Post.objects.filter(
            #Team: same team as the author
            read_permission='team',
            author__team=user.team
        ) | Post.objects.filter(
            #Owner: author
            read_permission='author',
            author=user
        )
    
class PostUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        post = super().get_object()
        user = self.request.user

        if not user_can_edit_post(user, post):
            raise PermissionDenied('You do not have permission to edit this post')
        
        return post
    
class PostDetailView(generics.RetrieveAPIView):
    serializer_class = PostDetailSerializer
    queryset = Post.objects.all()

    def get_object(self):
        post = super().get_object()
        user = self.request.user

        if not user_can_read_post(user, post):
            raise NotFound("Post Not Found")
        
        return post

class PostDeleteView(generics.DestroyAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def perform_destroy(self, instance):
        user = self.request.user

        if not user_can_edit_post(user, instance):
            raise PermissionDenied("You don't have permission to delete this post")
        
        instance.delete()