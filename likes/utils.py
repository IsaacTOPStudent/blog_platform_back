from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound
from .models import Post
from posts.permissions import user_can_read_post

def get_post_or_404_for_user(user, post_id):
    """
    Gets a post if it exists and also if that exists check if user had read permissions
    If it doesn't exist or the user doesn't have access, throws Not Found
    """

    post = get_object_or_404(Post, id=post_id)
    if not user_can_read_post(user, post):
        raise NotFound("Post Not Found")
    return post 