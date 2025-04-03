from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from issues.models import Issue, IssueImage
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class IssueModelTest(TestCase):
    """Test cases for the Issue model"""
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='test1234',
            type=User.UserType.CITIZEN
        )
        
        # Create a test issue
        self.test_issue = Issue.objects.create(
            reported_by=self.user,
            title='Test Issue',
            description='This is a test issue description',
            type=Issue.IssueType.INFRASTRUCTURE,
            location=Point(78.9629, 20.5937),  # longitude, latitude for center of India
            status=Issue.StatusType.PENDING,
            priority=Issue.PriorityType.NORMAL
        )
        
        # Create a test image for the issue
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        self.test_image = IssueImage.objects.create(
            issue=self.test_issue,
            image=SimpleUploadedFile('test.gif', small_gif, content_type='image/gif'),
            caption='Test Image'
        )
    
    def test_issue_creation_and_string_representation(self):
        """Test that issue is created correctly and has proper string representation"""
        # Check the issue was created
        self.assertEqual(Issue.objects.count(), 1)
        
        # Test issue fields
        self.assertEqual(self.test_issue.title, 'Test Issue')
        self.assertEqual(self.test_issue.reported_by, self.user)
        self.assertEqual(self.test_issue.type, Issue.IssueType.INFRASTRUCTURE)
        self.assertEqual(self.test_issue.status, Issue.StatusType.PENDING)
        
        # Check string representation
        self.assertEqual(str(self.test_issue), 'Test Issue (Pending)')
        
        # Check related issue image
        self.assertEqual(self.test_issue.images.count(), 1)
        self.assertEqual(self.test_issue.images.first(), self.test_image)
        self.assertEqual(str(self.test_image), 'Image for Test Issue')