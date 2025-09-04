from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'created_at', 'read_permission', 'edit_permission')
    list_filter = ('read_permission', 'edit_permission', 'created_at')
    search_fields = ('title', 'content', 'author__username')
