from django.contrib.auth.models import AbstractUser
from django.db import models

USER_TYPE = {
    ('CITIZEN', 'citizen'),
    ('MUNICIPAL', 'municipal'),
}

# Create your models here.
class User(AbstractUser):
    type = models.CharField(choices=USER_TYPE, max_length=20, blank=False)

    def __str__(self):
        return self.username