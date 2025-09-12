from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from likes.paginations_likes import LikePagination

from .models import Like
from .serializers import LikeSerializer, LikeActionSerializer
from likes.utils import get_post_or_404_for_user


class LikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LikeActionSerializer

    @extend_schema(
            operation_id='create_like',
            description='Like a post',
            request=LikeActionSerializer,
            responses={
            201: OpenApiResponse(
                response=LikeSerializer,
                description="Like created successfully"
            ),
            400: OpenApiResponse(description="You have already liked this post"),
            404: OpenApiResponse(description="Post not found"),
            },
            tags=['Likes'],
    )

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
    
    @extend_schema(
        operation_id="remove_like",
        description="Remove like from a post",
        responses={
            204: OpenApiResponse(description="Like deleted successfully"),
            400: OpenApiResponse(description="You have not liked this post"),
            404: OpenApiResponse(description="Post not found"),
        },
        tags=["Likes"],      
    )
    
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

    @extend_schema(
        operation_id='list_post_likes',
        description='Get all likes for a specific post',
        parameters=[
            OpenApiParameter(
                name='user_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filter likes by user ID'       
            )
        ],
        responses={
            200: OpenApiResponse(
                response=LikeSerializer(many=True),
                description="List of likes"
            ),
            404: OpenApiResponse(description="Post not found"),
        },
        tags=["Likes"],
    )     
    def get(self, request, *args, **kwargs):
        """Get all likes for a specific post with optional user filtering"""
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        user = self.request.user
        post = get_post_or_404_for_user(user, post_id)

        queryset = Like.objects.filter(post=post)

        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user__id=user_id)

        return queryset.order_by('-created_at')

