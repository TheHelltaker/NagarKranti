from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    Custom User model that extends Django's AbstractUser.
    Adds a user type field to distinguish between citizen and municipal users.
    """
    class UserType(models.TextChoices):
        CITIZEN = 'CITIZEN', _('Citizen')
        MUNICIPAL = 'MUNICIPAL', _('Municipal Officer')
    

    type = models.CharField(
        max_length=10,
        choices=UserType.choices,
        default=UserType.CITIZEN,
        verbose_name=_('User Type')
    )
    
    aadhaar_number = models.CharField(max_length=12, blank=True, null=True)
    phone_number = models.CharField(max_length=10, blank=True, null=True)
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
    
    def is_municipal_user(self):
        """Check if the user is a municipal officer"""
        return self.type == self.UserType.MUNICIPAL
    
    def is_citizen_user(self):
        """Check if the user is a citizen"""
        return self.type == self.UserType.CITIZEN
    
    def __str__(self):
        return f"{self.username} ({self.get_type_display()})"