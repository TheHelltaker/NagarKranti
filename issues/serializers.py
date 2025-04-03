from rest_framework import serializers
from django.contrib.gis.geos import Point
from .models import Issue, IssueImage

class IssueImageSerializer(serializers.ModelSerializer):
    """Serializer for issue images"""
    class Meta:
        model = IssueImage
        fields = ['id', 'image', 'caption', 'uploaded_at']
        read_only_fields = ['uploaded_at']

class IssueSerializer(serializers.ModelSerializer):
    """
    Serializer for issues with nested image serializer.
    Used for read operations (list and retrieve).
    """
    images = IssueImageSerializer(many=True, read_only=True)
    reported_by_username = serializers.CharField(source='reported_by.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    # For coordinate representation
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    
    class Meta:
        model = Issue
        fields = [
            'id', 'title', 'description', 'type', 'type_display',
            'status', 'status_display', 'priority', 'priority_display',
            'reported_by', 'reported_by_username', 'location', 
            'latitude', 'longitude', 'images',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['reported_by', 'created_at', 'updated_at']
    
    def get_latitude(self, obj):
        return obj.location.y if obj.location else None
    
    def get_longitude(self, obj):
        return obj.location.x if obj.location else None

class IssueCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating issues with location data and images.
    """
    images = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        write_only=True
    )
    latitude = serializers.FloatField(write_only=True, required=True)
    longitude = serializers.FloatField(write_only=True, required=True)
    
    class Meta:
        model = Issue
        fields = [
            'title', 'description', 'type', 'latitude', 'longitude',
            'images'
        ]
    
    def validate(self, data):
        # Make sure both latitude and longitude are provided
        if 'latitude' not in data or 'longitude' not in data:
            raise serializers.ValidationError(
                "Both latitude and longitude are required."
            )
        return data
    
    def create(self, validated_data):
        # Extract and remove images from validated data
        images_data = validated_data.pop('images', [])
        
        # Extract and remove coordinates to create Point object
        latitude = validated_data.pop('latitude')
        longitude = validated_data.pop('longitude')
        location = Point(longitude, latitude, srid=4326)
        
        # Add location and user to validated data
        validated_data['location'] = location
        validated_data['reported_by'] = self.context['request'].user
        
        # Create issue instance
        issue = Issue.objects.create(**validated_data)
        
        # Create issue images
        for image_data in images_data:
            IssueImage.objects.create(issue=issue, image=image_data)
        
        return issue

class IssueUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating issue status and priority.
    Used primarily by municipal users.
    """
    class Meta:
        model = Issue
        fields = ['status', 'priority']
    
    def validate(self, data):
        """
        Validate that only municipal users can update issue status
        """
        user = self.context['request'].user
        if not user.is_municipal_user() and 'status' in data:
            raise serializers.ValidationError(
                {"status": "Only municipal officers can update issue status."}
            )
        return data

class AddIssueImageSerializer(serializers.ModelSerializer):
    """
    Serializer for adding additional images to an existing issue.
    """
    image = serializers.ImageField(required=True)
    
    class Meta:
        model = IssueImage
        fields = ['image', 'caption']
    
    def create(self, validated_data):
        issue_id = self.context['issue_id']
        validated_data['issue_id'] = issue_id
        return IssueImage.objects.create(**validated_data)

class NearbyIssueSerializer(serializers.Serializer):
    """
    Serializer for finding issues near a specific location.
    """
    latitude = serializers.FloatField(required=True)
    longitude = serializers.FloatField(required=True)
    distance = serializers.IntegerField(required=False, default=5000)  # Default 5km