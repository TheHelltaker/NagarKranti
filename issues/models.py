
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

# Create your models here.
class Issue(models.Model):
    """
    Model for storing issue/complaint data reported by citizens.
    Includes geographic location and issue status tracking.
    """
    class IssueType(models.TextChoices):
        INFRASTRUCTURE = 'INFRASTRUCTURE', _('Infrastructure')
        SERVICES = 'SERVICES', _('Services')
        ENCROACHMENT = 'ENCROACHMENT', _('Encroachment')
        OTHER = 'OTHER', _('Other')
    
    class StatusType(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        ACCEPTED = 'ACCEPTED', _('Accepted')
        IN_PROGRESS = 'IN PROGRESS', _('In Progress')
        RESOLVED = 'RESOLVED', _('Resolved')
    
    class PriorityType(models.TextChoices):
        HIGH = 'HIGH', _('High')
        NORMAL = 'NORMAL', _('Normal')
        LOW = 'LOW', _('Low')
        NA = 'NA', _('Not Applicable')
    
    # Foreign Key to User model
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reported_issues',
        verbose_name=_('Reported By')
    )
    
    # Basic issue details
    title = models.CharField(max_length=100, verbose_name=_('Title'))
    description = models.TextField(verbose_name=_('Description'))
    type = models.CharField(
        max_length=15,
        choices=IssueType.choices,
        default=IssueType.OTHER,
        verbose_name=_('Issue Type')
    )
    
    # Location data
    location = gis_models.PointField(verbose_name=_('Location'))
    
    # Status and tracking
    status = models.CharField(
        max_length=15,
        choices=StatusType.choices,
        default=StatusType.PENDING,
        verbose_name=_('Status')
    )
    priority = models.CharField(
        max_length=10,
        choices=PriorityType.choices,
        default=PriorityType.NORMAL,
        verbose_name=_('Priority')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    
    class Meta:
        verbose_name = _('Issue')
        verbose_name_plural = _('Issues')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

class IssueImage(models.Model):
    """
    Model for storing images associated with an issue.
    """
    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('Issue')
    )
    image = models.ImageField(
        upload_to='issue_images/%Y/%m/%d/',
        verbose_name=_('Image')
    )
    caption = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Caption')
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Uploaded At')
    )
    
    class Meta:
        verbose_name = _('Issue Image')
        verbose_name_plural = _('Issue Images')
        ordering = ['uploaded_at']
    
    def __str__(self):
        return f"Image for {self.issue.title}"