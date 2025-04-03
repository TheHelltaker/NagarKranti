from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationAPITest(APITestCase):
    """Test case for user registration API"""
    
    def setUp(self):
        self.register_url = reverse('register')
        self.valid_citizen_data = {
            'username': 'newcitizen',
            'email': 'newcitizen@example.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'first_name': 'New',
            'last_name': 'Citizen',
            'type': User.UserType.CITIZEN
        }
        
        # Create a municipal user for testing
        self.municipal_user = User.objects.create_user(
            username='testmunicipal',
            email='municipal@example.com',
            password='test1234',
            type=User.UserType.MUNICIPAL
        )
    
    def test_user_registration(self):
        """Test that a user can be registered via the API"""
        # Initial user count
        initial_user_count = User.objects.count()
        
        # Register a new citizen user
        response = self.client.post(self.register_url, self.valid_citizen_data, format='json')
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify a new user was created
        self.assertEqual(User.objects.count(), initial_user_count + 1)
        
        # Verify user details
        new_user = User.objects.get(username='newcitizen')
        self.assertEqual(new_user.email, 'newcitizen@example.com')
        self.assertEqual(new_user.first_name, 'New')
        self.assertEqual(new_user.last_name, 'Citizen')
        self.assertEqual(new_user.type, User.UserType.CITIZEN)
        self.assertTrue(new_user.is_citizen_user())