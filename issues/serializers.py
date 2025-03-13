from rest_framework import serializers
from .models import Issue

class IssueSerializer(serializers.HyperlinkedModelSerializer):
    # This field shows which user reported the issue (read-only)
    reported_by = serializers.HyperlinkedRelatedField(
        view_name='user-detail',
        read_only=True
    )

    class Meta:
        model = Issue
        fields = [
            'url',
            'id',
            'created_at',
            'updated_at',
            'type',
            'title',
            'description',
            'location',
            'status',
            'priority',
            'reported_by',
        ]
