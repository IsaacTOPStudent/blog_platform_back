from django.contrib import admin
from django import forms
from .models import User, Team
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm

class CustomUserChangeForm(UserChangeForm):
    username = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={ 'autofocus': True })
    )

    class Meta(UserChangeForm.Meta):
        model = User
        fields = '__all__'
    
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # Allow username to be optional and handle None values
    #     if 'username' in self.fields:
    #         self.fields['username'].required = False
    #         # Remove validators that don't handle None
    #         self.fields['username'].validators = []
    
    def clean_username(self):
        """Handle None username values properly"""
        username = self.cleaned_data.get('username')
        # Convert empty string to None for consistency
        if not username:
            return None
        return username

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('role', 'team', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'team'),
        }),
    )
    list_display = ('email', 'username', 'role', 'team', 'is_staff', 'is_active')
    list_filter = ('role', 'team', 'is_staff', 'is_active')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')