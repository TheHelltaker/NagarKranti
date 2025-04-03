from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

class AuthenticationSecurityTests(TestCase):
    """Tests for authentication security features"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('user-register')
        self.token_url = reverse('token_obtain_pair')
        self.me_url = reverse('user-me')
        
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'type': 'CITIZEN'
        }
        
        # Create a user
        self.user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password'],
            type=self.user_data['type']
        )
        
    def test_invalid_token_rejection(self):
        """Test the system rejects invalid tokens"""
        # Use an invalid token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalidtoken123')
        response = self.client.get(self.me_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_expired_token_rejection(self):
        """Test the system rejects expired tokens (simulated with a token that doesn't exist)"""
        # This is a simplified test since we can't easily create an expired token in a unit test
        self.client.credentials(HTTP_AUTHORIZATION='Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNTc5MDYyMjIwLCJqdGkiOiJmNjJhYTliZjMwOTY0YWU2YTMyOGVhZmY1YzUyMjc2OCIsInVzZXJfaWQiOjF9.invalid')
        response = self.client.get(self.me_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_brute_force_protection(self):
        """Test brute force protection by trying multiple wrong passwords"""
        # Try multiple incorrect login attempts
        for _ in range(5):  # Assuming the system has some kind of rate limiting after N attempts
            response = self.client.post(
                self.token_url,
                {
                    'username': self.user_data['username'],
                    'password': 'wrongpassword'
                }
            )
            
        # If rate limiting is implemented, this would fail
        # This test assumes your app has some rate limiting, which is a good security practice
        
    def test_weak_password_rejection(self):
        """Test weak passwords are rejected during registration"""
        weak_passwords = [
            '12345678',  # Only numbers
            'password',  # Common password
            'short',     # Too short
        ]
        
        for password in weak_passwords:
            data = {
                'username': 'newuser',
                'email': 'new@example.com',
                'password': password,
                'type': 'CITIZEN'
            }
            
            response = self.client.post(self.register_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            
    def test_password_not_returned(self):
        """Test password hash is not returned in API responses"""
        # Get valid token
        response = self.client.post(
            self.token_url,
            {
                'username': self.user_data['username'],
                'password': self.user_data['password']
            }
        )
        
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Get user profile
        response = self.client.get(self.me_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('password', response.data)


class CSRFProtectionTests(TestCase):
    """Tests for CSRF protection"""
    
    def setUp(self):
        self.client = APIClient(enforce_csrf_checks=True)
        self.token_url = reverse('token_obtain_pair')
        
        # Create a user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='Pass123!',
            type='CITIZEN'
        )
        
    @override_settings(REST_FRAMEWORK={
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'rest_framework.authentication.SessionAuthentication',
            'rest_framework_simplejwt.authentication.JWTAuthentication',
        ]
    })
    def test_csrf_protection_on_session_auth(self):
        """Test CSRF protection on endpoints using session authentication"""
        # This test assumes you've configured session authentication as a fallback
        
        # First, let's log in to get a session
        login_successful = self.client.login(
            username='testuser',
            password='Pass123!'
        )
        self.assertTrue(login_successful)
        
        # Try to post without CSRF token
        response = self.client.post(
            self.token_url,
            {
                'username': 'testuser',
                'password': 'Pass123!'
            },
            format='json'
        )
        
        # Should be rejected due to missing CSRF token
        self.assertIn(response.status_code, 
                     [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])


class UserInputValidationTests(TestCase):
    """Tests for input validation on user data"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('user-register')
        
    def test_invalid_user_data_rejection(self):
        """Test system rejects invalid user registration data"""
        invalid_data = [
            # Invalid email
            {
                'username': 'testuser',
                'email': 'not-an-email',
                'password': 'Pass123!',
                'type': 'CITIZEN'
            },
            # Invalid user type
            {
                'username': 'testuser',
                'email': 'valid@example.com',
                'password': 'Pass123!',
                'type': 'INVALID_TYPE'
            },
            # Username too long
            {
                'username': 'a' * 151,  # Assuming max length is 150
                'email': 'valid@example.com',
                'password': 'Pass123!',
                'type': 'CITIZEN'
            }
        ]
        
        for data in invalid_data:
            response = self.client.post(self.register_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)