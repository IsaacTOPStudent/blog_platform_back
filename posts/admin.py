from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'created_at', 'author_access', 'team_access', 'authenticated_access', 'public_access')
    list_filter = ('author_access', 'team_access', 'authenticated_access', 'public_access', 'created_at')
    search_fields = ('title', 'content', 'author__username')
