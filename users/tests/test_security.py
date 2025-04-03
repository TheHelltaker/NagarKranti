from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class UserPermissionsTest(APITestCase):
    """Test case for permission checks in the user API"""
    
    def setUp(self):
        # Create test users
        self.citizen_user = User.objects.create_user(
            username='testcitizen',
            email='citizen@example.com',
            password='test1234',
            type=User.UserType.CITIZEN
        )
        
        self.municipal_user = User.objects.create_user(
            username='testmunicipal',
            email='municipal@example.com',
            password='test1234',
            type=User.UserType.MUNICIPAL
        )
        
        self.another_citizen = User.objects.create_user(
            username='anothercitizen',
            email='another@example.com',
            password='test1234',
            type=User.UserType.CITIZEN
        )
        
        # URLs for testing
        self.users_list_url = reverse('user-list')
        self.citizen_detail_url = reverse('user-detail', kwargs={'pk': self.citizen_user.pk})
    
    def test_citizen_user_permissions(self):
        """Test that citizen users can only view their own profile"""
        # Login as citizen user
        self.client.force_authenticate(user=self.citizen_user)
        
        # Citizen should not be able to see list of all users
        response = self.client.get(self.users_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Citizen should be able to view their own profile
        response = self.client.get(reverse('user-detail', kwargs={'pk': self.citizen_user.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Citizen should not be able to view other user's profile
        response = self.client.get(reverse('user-detail', kwargs={'pk': self.another_citizen.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)