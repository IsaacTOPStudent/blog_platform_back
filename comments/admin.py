from django.contrib import admin
from .models import Comment

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'content', 'created_at')
    search_fields = ('content', 'user__username', 'post__title')
    list_filter = ('created_at',)
