from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserModelTests(TestCase):
    """Tests for the custom User model"""
    
    def setUp(self):
        self.citizen_data = {
            'username': 'testcitizen',
            'email': 'citizen@example.com',
            'password': 'securepass123',
            'type': 'CITIZEN'
        }
        self.municipal_data = {
            'username': 'testmunicipal',
            'email': 'municipal@example.com',
            'password': 'securepass123',
            'type': 'MUNICIPAL'
        }
        
    def test_create_citizen_user(self):
        """Test creating a citizen user is successful"""
        user = User.objects.create_user(**self.citizen_data)
        
        self.assertEqual(user.username, self.citizen_data['username'])
        self.assertEqual(user.email, self.citizen_data['email'])
        self.assertEqual(user.type, 'CITIZEN')
        self.assertTrue(user.check_password(self.citizen_data['password']))
        self.assertFalse(user.is_staff)
        
    def test_create_municipal_user(self):
        """Test creating a municipal user is successful"""
        user = User.objects.create_user(**self.municipal_data)
        
        self.assertEqual(user.username, self.municipal_data['username'])
        self.assertEqual(user.email, self.municipal_data['email'])
        self.assertEqual(user.type, 'MUNICIPAL')
        self.assertTrue(user.check_password(self.municipal_data['password']))
        self.assertTrue(user.is_staff)  # Municipal users should be staff
        
    def test_email_normalization(self):
        """Test email is normalized when creating a user"""
        email = 'test@EXAMPLE.com'
        user = User.objects.create_user(username='test', email=email, password='test123')
        
        self.assertEqual(user.email, email.lower())
        
    def test_create_superuser(self):
        """Test creating a superuser"""
        user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)