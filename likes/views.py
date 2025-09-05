from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from likes.paginations_likes import LikePagination

from .models import Like
from .serializers import LikeSerializer
from likes.utils import get_post_or_404_for_user


class LikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        """
        Add like to a post (if user has view access)
        """
        #all logic about gets object or user can read the post is here
        post = get_post_or_404_for_user(request.user, post_id)
        
        #prevent multiple likes
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            return Response({'detail': 'You have already liked this post'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = LikeSerializer(like)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def delete(self, request, post_id):
        """
        Remove a like from a post (if it exists)
        """
        post = get_post_or_404_for_user(request.user, post_id)

        like = Like.objects.filter(user=request.user, post=post).first()
        if not like:
            return Response({'detail': 'You have not liked this post.'}, status=status.HTTP_400_BAD_REQUEST)
        
        like.delete()
        return Response({'detail': 'Like removed successfully.'}, status=status.HTTP_204_NO_CONTENT)
    
class LikeListView(generics.ListAPIView):
    serializer_class = LikeSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = LikePagination 

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        user = self.request.user
        post = get_post_or_404_for_user(user, post_id)

        queryset = Like.objects.filter(post=post)

        user_id = self.request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(user__id=user_id)

        return queryset

