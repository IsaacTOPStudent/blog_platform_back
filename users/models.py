from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ObjectDoesNotExist
# Create your models here.

class  Team(models.Model):
    name = models.CharField(max_length=50, unique= True)

    def __str__(self):
        return self.name
    
class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Please enter an email address")
        email = self.normalize_email(email)
        extra_fields.setdefault('username', '')

        if 'team' not in extra_fields or extra_fields['team'] is None:
            try:
                default_team = Team.objects.get(name='Default Team')
            except ObjectDoesNotExist:
                default_team = Team.objects.create(name='Default Team')
            extra_fields['team'] = default_team
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

    
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('blogger', 'Blogger'),
    )
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, blank=True, null=True, default=None)

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='blogger')
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank= True, related_name='members')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['username', 'team'], name='unique_username_team')
        ]

    def __str__(self):
        display_name = self.username if self.username else self.email
        return f"{display_name} ({self.role})"
                                                    