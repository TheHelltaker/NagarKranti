from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer for viewing user information"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'type', 'date_joined', 'last_login']
        read_only_fields = ['date_joined', 'last_login']

class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users with password validation"""
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'password2', 'email', 'first_name', 
                  'last_name', 'type']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        # Remove password2 from validated data
        validated_data.pop('password2')
        
        # Create user with validated data
        user = User.objects.create_user(**validated_data)
        return user

class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError(
                {"new_password": "Password fields didn't match."}
            )
        return attrs
        
class UpdateUserSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']