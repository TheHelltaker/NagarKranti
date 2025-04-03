from django.contrib.auth import get_user_model
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    UserSerializer, 
    UserCreateSerializer, 
    ChangePasswordSerializer,
    UpdateUserSerializer
)
from .permissions import IsMunicipalUser, IsOwnerOrMunicipal

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    Allows anyone to register as a citizen or municipal user.
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserCreateSerializer

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user management.
    - Municipal users can view all users
    - Citizens can only view and update their own profile
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """
        Override permissions based on the action:
        - list: only municipal users can list all users
        - retrieve/update/partial_update: owner or municipal users
        - destroy: only municipal users
        """
        if self.action == 'list':
            permission_classes = [IsAuthenticated, IsMunicipalUser]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            permission_classes = [IsAuthenticated, IsOwnerOrMunicipal]
        elif self.action == 'destroy':
            permission_classes = [IsAuthenticated, IsMunicipalUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action in ['update', 'partial_update']:
            return UpdateUserSerializer
        return UserSerializer
    
    def get_queryset(self):
        """
        Filter queryset based on user type:
        - Municipal users can see all users
        - Citizens can only see their own profile
        """
        user = self.request.user
        if user.is_municipal_user():
            return User.objects.all()
        return User.objects.filter(id=user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Return the authenticated user's profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], serializer_class=ChangePasswordSerializer)
    def change_password(self, request):
        """Change password endpoint"""
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            # Check old password
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({"old_password": ["Wrong password."]}, 
                                status=status.HTTP_400_BAD_REQUEST)
            
            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": "Password changed successfully."}, 
                           status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)