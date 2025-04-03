from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.db.models import Q
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from .models import Issue, IssueImage
from .serializers import (
    IssueSerializer, 
    IssueCreateSerializer,
    IssueUpdateSerializer, 
    IssueImageSerializer,
    AddIssueImageSerializer,
    NearbyIssueSerializer
)
from users.permissions import IsMunicipalUser, IsOwnerOrMunicipal

class IssueViewSet(viewsets.ModelViewSet):
    """
    API endpoint for issue management.
    Supports CRUD operations with different permissions based on user type:
    - Citizens can create issues and view their own issues
    - Municipal users can view, update, and delete any issue
    """
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]  # Added JSONParser
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type', 'status', 'priority']
    
    def get_queryset(self):
        """
        Filter queryset based on user type:
        - Municipal users can see all issues
        - Citizens can only see their own issues
        """
        user = self.request.user
        if user.is_municipal_user():
            return Issue.objects.all()
        return Issue.objects.filter(reported_by=user)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return IssueCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return IssueUpdateSerializer
        elif self.action == 'nearby':
            return NearbyIssueSerializer
        return IssueSerializer
    
    def get_permissions(self):
        """
        Override permissions based on the action:
        - create: any authenticated user can create issues
        - list/retrieve: owner or municipal users
        - update/partial_update: owner (only status) or municipal users (all fields)
        - destroy: only municipal users
        """
        if self.action in ['retrieve', 'list', 'create', 'update', 'partial_update']:
            permission_classes = [IsAuthenticated, IsOwnerOrMunicipal]
        elif self.action == 'destroy':
            permission_classes = [IsAuthenticated, IsMunicipalUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        """
        method to handle both JSON and form data
        """
        if request.content_type == 'application/json':
            # Handle JSON data
            data = request.data
            serializer_data = {
                'title': data.get('title'),
                'description': data.get('description'),
                'type': data.get('issue_type', 'OTHER'),  # Map issue_type to type
                'latitude': None,
                'longitude': None
            }
            
            # Extract coordinates from location object if present
            location = data.get('location', {})
            if location and 'coordinates' in location:
                # GeoJSON has [longitude, latitude] order
                serializer_data['longitude'] = location['coordinates'][0]
                serializer_data['latitude'] = location['coordinates'][1]
            
            serializer = self.get_serializer(data=serializer_data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            # Proceed with standard form data handling
            return super().create(request, *args, **kwargs)
    
    @action(detail=False, methods=['post'])
    def nearby(self, request):
        """
        Find issues near a specific location.
        Accepts latitude, longitude, and optional distance (in meters).
        """
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            latitude = serializer.validated_data['latitude']
            longitude = serializer.validated_data['longitude']
            distance = serializer.validated_data.get('distance', 5000)  # Default 5km
            
            # Create point from coordinates
            point = Point(longitude, latitude, srid=4326)
            
            # Query issues within distance
            queryset = self.get_queryset().annotate(
                distance=Distance('location', point)
            ).filter(distance__lte=distance).order_by('distance')
            
            # Serialize results
            issue_serializer = IssueSerializer(queryset, many=True)
            return Response(issue_serializer.data)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_image(self, request, pk=None):
        """
        Add a new image to an existing issue.
        Only the issue owner or municipal users can add images.
        """
        issue = self.get_object()
        serializer = AddIssueImageSerializer(
            data=request.data,
            context={'issue_id': issue.id}
        )
        
        if serializer.is_valid():
            image = serializer.save()
            return Response(
                IssueImageSerializer(image).data,
                status=status.HTTP_201_CREATED
            )
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class IssueImageViewSet(mixins.RetrieveModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    """
    API endpoint for retrieving and deleting issue images.
    Only the issue owner or municipal users can delete images.
    """
    queryset = IssueImage.objects.all()
    serializer_class = IssueImageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['retrieve', 'destroy']:
            permission_classes = [IsAuthenticated, IsOwnerOrMunicipal]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def destroy(self, request, *args, **kwargs):
        """
        Override destroy to check if the user is the issue owner or a municipal user
        """
        instance = self.get_object()
        
        # Check permissions
        if not (request.user.is_municipal_user() or 
                instance.issue.reported_by == request.user):
            return Response(
                {"detail": "You don't have permission to delete this image."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        return super().destroy(request, *args, **kwargs)