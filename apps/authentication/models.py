# apps/authentication/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.common.models import TimeStampedModel

class User(AbstractUser, TimeStampedModel):
    """Custom User model with farm assignment and role management"""
    
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('farmer', 'Farmer'),
    ]
    
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='farmer')
    is_active = models.BooleanField(default=True)
    assigned_farm = models.ForeignKey(
        'farms.Farm', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='farmers'
    )
    profile_picture = models.ImageField(
        upload_to='user_profiles/', 
        null=True, 
        blank=True
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_farmer(self):
        return self.role == 'farmer'
    
    def can_access_farm(self, farm):
        """Check if user can access a specific farm"""
        if self.is_admin:
            return True
        return self.assigned_farm == farm
