from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from .models import Issue, IssueImage

class IssueImageInline(admin.TabularInline):
    """Inline admin for issue images"""
    model = IssueImage
    extra = 0

@admin.register(Issue)
class IssueAdmin(GISModelAdmin):
    """Admin interface for issues with map display"""
    list_display = (
        'id', 'title', 'type', 'status', 'priority', 
        'reported_by', 'created_at', 'updated_at'
    )
    list_filter = ('type', 'status', 'priority', 'created_at')
    search_fields = ('title', 'description', 'reported_by__username')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    inlines = [IssueImageInline]

    # gis_widget_kwargs = {
    #     'default_lat': 20.5937,   # Latitude for center of India
    #     'default_lon': 78.9629,   # Longitude for center of India
    #     'default_zoom': 5
    # }

@admin.register(IssueImage)
class IssueImageAdmin(admin.ModelAdmin):
    """Admin interface for issue images"""
    list_display = ('id', 'issue', 'caption', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('caption', 'issue__title')
    readonly_fields = ('uploaded_at',)