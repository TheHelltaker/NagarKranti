from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserModelTest(TestCase):
    """Test cases for the custom User model"""
    
    def setUp(self):
        # Create test users
        self.citizen_user = User.objects.create_user(
            username='testcitizen',
            email='citizen@example.com',
            password='test1234',
            type=User.UserType.CITIZEN,
            aadhaar_number='123456789012',
            phone_number='9876543210'
        )
        
        self.municipal_user = User.objects.create_user(
            username='testmunicipal',
            email='municipal@example.com',
            password='test1234',
            type=User.UserType.MUNICIPAL
        )
    
    def test_user_type_methods(self):
        """Test the is_citizen_user and is_municipal_user helper methods"""
        # Verify citizen user type
        self.assertTrue(self.citizen_user.is_citizen_user())
        self.assertFalse(self.citizen_user.is_municipal_user())
        
        # Verify municipal user type
        self.assertTrue(self.municipal_user.is_municipal_user())
        self.assertFalse(self.municipal_user.is_citizen_user())
        
        # Check string representation
        self.assertEqual(str(self.citizen_user), "testcitizen (Citizen)")
        self.assertEqual(str(self.municipal_user), "testmunicipal (Municipal Officer)")