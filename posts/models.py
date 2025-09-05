from django.db import models

from django.conf import settings

User = settings.AUTH_USER_MODEL

class Post(models.Model):
    PERMISSION_CHOICES = (
        ('public', 'Public'),
        ('authenticated', 'Authenticated'),
        ('team', 'Team'),
        ('author', 'Author'),
    )

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    excerpt = models.TextField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add= True)
    update_at = models.DateTimeField(auto_now= True)
    likes_count = models.PositiveIntegerField(default=0)

    read_permission = models.CharField(max_length=20, choices=PERMISSION_CHOICES, default='public')
    edit_permission = models.CharField(max_length=20, choices=PERMISSION_CHOICES, default='author')

    def save(self, *args, **kwargs):
        if not self.excerpt:
            self.excerpt = self.content[:200]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.author})"