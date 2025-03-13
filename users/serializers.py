from rest_framework import serializers
from .models import User
from issues.serializers import IssueSerializer

class UserSerializer(serializers.HyperlinkedModelSerializer):
    # This will show all issues that the user has reported.
    issues = IssueSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'url',
            'id',
            'username',
            'type',
            'issues',
        ]

# New Registration Serializer
class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'type']

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            type=validated_data['type'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user