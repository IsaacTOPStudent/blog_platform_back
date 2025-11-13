from django.db import models
from django.conf import settings
from django.utils.html import strip_tags

User = settings.AUTH_USER_MODEL

class Post(models.Model):
    AUTHOR_CHOICES = [
        ('write', 'Read & Write'),
    ]

    TEAM_AUTH_CHOICES = [
        ('none', 'None'),
        ('read', 'Read Only'),
        ('write', 'Read & Write'),
    ]

    PUBLIC_CHOICES = [
        ('none', 'None'),
        ('read', 'Read Only'),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    excerpt = models.TextField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add= True)
    update_at = models.DateTimeField(auto_now= True)
    likes_count = models.PositiveIntegerField(default=0)

    public_access = models.CharField(
        max_length=10, choices= PUBLIC_CHOICES,
        default='none'
    )

    authenticated_access = models.CharField(
        max_length=10, choices=TEAM_AUTH_CHOICES,
        default='none'
    )

    team_access = models.CharField(
        max_length=10, choices=TEAM_AUTH_CHOICES,
        default='none'
    )

    author_access = models.CharField(
        max_length=10, choices=AUTHOR_CHOICES,
        default='write'
    )

    def save(self, *args, **kwargs):
        # Always regenerate excerpt from current content (strip HTML safely without external deps)
        text = strip_tags(self.content or '')
        text = ' '.join(text.split())  # normalize whitespace
        if len(text) > 200:
            cut = text[:200]
            cut = cut.rsplit(' ', 1)[0] if ' ' in cut else cut
            self.excerpt = f"{cut}..."
        else:
            self.excerpt = text
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.author})"
    
    class Meta:
        ordering = ['-created_at']