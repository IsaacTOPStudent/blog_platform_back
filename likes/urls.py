from django.urls import path
from .views import LikeView, LikeListView

urlpatterns = [
    path('post/<int:post_id>/like/', LikeView.as_view(), name='like-unlike-post-delete'),
    path('post/<int:post_id>/likes/', LikeListView.as_view(), name='list-likes'),
]