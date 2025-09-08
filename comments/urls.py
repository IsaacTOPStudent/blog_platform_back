from django.urls import path
from .views import CommentCreateView, CommentDeleteView, CommentListView

urlpatterns = [
    path('post/<int:post_id>/comment/', CommentCreateView.as_view(), name='comment-create'),
    path('comment/<int:pk>/', CommentDeleteView.as_view(), name='comment-delete'),
    path('post/<int:post_id>/comments/', CommentListView.as_view(), name='comment-list')
]