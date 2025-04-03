from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

class AuthenticationAPITests(TestCase):
    """Tests for the authentication API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('user-register')
        self.token_url = reverse('token_obtain_pair')
        self.refresh_url = reverse('token_refresh')
        
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'type': 'CITIZEN'
        }
        
    def test_user_registration(self):
        """Test that user registration works"""
        response = self.client.post(self.register_url, self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username=self.user_data['username']).exists())
        
    def test_user_registration_invalid_data(self):
        """Test registration fails with invalid data"""
        # Missing required field
        invalid_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_token_obtain(self):
        """Test obtaining JWT token"""
        # Create a user first
        user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password'],
            type=self.user_data['type']
        )
        
        # Attempt to get token
        response = self.client.post(
            self.token_url,
            {
                'username': self.user_data['username'],
                'password': self.user_data['password']
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
    def test_token_refresh(self):
        """Test refreshing JWT token"""
        # Create a user first
        user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password'],
            type=self.user_data['type']
        )
        
        # Get token
        response = self.client.post(
            self.token_url,
            {
                'username': self.user_data['username'],
                'password': self.user_data['password']
            }
        )
        
        # Refresh token
        refresh_token = response.data['refresh']
        response = self.client.post(
            self.refresh_url,
            {'refresh': refresh_token}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)


class UserProfileAPITests(TestCase):
    """Tests for the user profile API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.me_url = reverse('user-me')
        
        # Create citizen and municipal users
        self.citizen = User.objects.create_user(
            username='citizen',
            email='citizen@example.com',
            password='pass123',
            type='CITIZEN'
        )
        
        self.municipal = User.objects.create_user(
            username='municipal',
            email='municipal@example.com',
            password='pass123',
            type='MUNICIPAL'
        )
        
    def test_retrieve_profile_authenticated(self):
        """Test authenticated users can retrieve their profile"""
        self.client.force_authenticate(user=self.citizen)
        response = self.client.get(self.me_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.citizen.username)
        self.assertEqual(response.data['email'], self.citizen.email)
        self.assertEqual(response.data['type'], self.citizen.type)
        
    def test_retrieve_profile_unauthenticated(self):
        """Test unauthenticated users cannot retrieve profile"""
        response = self.client.get(self.me_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_update_profile(self):
        """Test updating user profile"""
        self.client.force_authenticate(user=self.citizen)
        payload = {
            'email': 'newemail@example.com',
        }
        
        response = self.client.patch(self.me_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.citizen.refresh_from_db()
        self.assertEqual(self.citizen.email, payload['email'])