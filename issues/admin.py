from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from issues.models import Issue

@admin.register(Issue)
class IssueAdmin(GISModelAdmin):
    list_display = (
        'title',
        'location',
        'status',
    )