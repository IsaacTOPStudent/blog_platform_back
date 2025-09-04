from django.contrib import admin
from .models import User, Team
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('role', 'team')}),
    )
    list_display = ('username', 'email', 'role', 'team', 'is_staff', 'is_active')
    list_filter = ('role', 'team', 'is_staff', 'is_active')

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')