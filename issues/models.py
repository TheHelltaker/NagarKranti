from django.contrib.gis.db import models
from users.models import User
from django.conf import settings

ISSUE_TYPES = [
    ('INFRASTRUCTURE','infrastructure'),
    ('ENCROACHMENT','encroachment'),
    ('SERVICES','services'),
    ('OTHER','other'),
]

STATUS_FLAGS = [
    ('PENDING', 'pending'),
    ('ACCEPETED', 'accepeted'),
    ('IN PROGRESS', 'in progress'),
    ('RESOLVED', 'resolved'),
]

PRIORITY_FLAGS = [
    ('HIGH', 'high'),
    ('NORMAL', 'normal'),
    ('LOW', 'low'),
    ('NA', 'na')
]


# Create your models here.
class Issue(models.Model):
    '''
    Issue model with the following attributes :

    reported_by : foreign key USER
    created_at : date and time of creation
    updated_at : last status update
    type : type of the Issue report
    title : title of the Issue report
    description : description of the Issue report
    location : location of the issue report
    status : status of the issue report
    priority : priority set by municipal admin or AI handler

    '''
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='issues',
        on_delete=models.CASCADE,
        default='nkadmin',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    type = models.CharField(choices=ISSUE_TYPES, max_length=50)
    title = models.CharField(max_length=100)
    description = models.TextField()
    location = models.PointField()
    status = models.CharField(choices=STATUS_FLAGS, max_length=50, default='submitted')
    priority = models.CharField(choices=PRIORITY_FLAGS, max_length=10, default='na')

    class Meta:
        ordering = ['created_at']