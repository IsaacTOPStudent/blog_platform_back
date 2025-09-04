from django.db import models
from django.conf import settings
from posts.models import Post

User = settings.AUTH_USER_MODEL

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post') #a user can only give one like per post.


    def __str__(self):
        return f"{self.user} likes {self.post.title}"
    