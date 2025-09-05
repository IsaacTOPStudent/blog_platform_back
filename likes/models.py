from django.db import models
from django.conf import settings
from posts.models import Post

User = settings.AUTH_USER_MODEL

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'post'], name= 'unique_user_post_like')
        ] #a user can only give one like per post.
        ordering = ['-created_at'] #most recently first


    def __str__(self):
        return f"{self.user.email} likes {self.post.title[:30]}"
    