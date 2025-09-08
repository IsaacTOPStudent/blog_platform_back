from django.urls import path
from .views import PostListCreateView, PostUpdateView, PostDetailView, PostDeleteView


urlpatterns = [
    path('post/', PostListCreateView.as_view(), name='post-list-create'),
    path('blog/<int:pk>/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='delete-post')
]