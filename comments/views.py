from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied, ValidationError
from .models import Comment
from .patinationsComments import CommentPagination
from .serializers import CommentSerializer
from likes.utils import get_post_or_404_for_user

class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

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
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = CommentPagination

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
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.all()
    
    def perform_destroy(self, instance):
         user = self.request.user
         if instance.user != user and not user.is_superuser:
             raise PermissionDenied('Only author or admin can delete this comment.')
         instance.delete()
