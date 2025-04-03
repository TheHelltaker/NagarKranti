from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.core.files.uploadedfile import SimpleUploadedFile
from issues.models import Issue, IssueImage

User = get_user_model()

class IssueModelTests(TestCase):
    """Tests for the Issue model"""
    
    def setUp(self):
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
        self.location = Point(78.4867, 17.3850)  # Example coordinates for Hyderabad
        
    def test_create_issue(self):
        """Test creating an issue is successful"""
        issue = Issue.objects.create(
            title='Test Issue',
            description='This is a test issue',
            location=self.location,
            issue_type='INFRASTRUCTURE',
            status='PENDING',
            priority='NORMAL',
            reporter=self.citizen
        )
        
        self.assertEqual(issue.title, 'Test Issue')
        self.assertEqual(issue.status, 'PENDING')
        self.assertEqual(issue.reporter, self.citizen)
        self.assertEqual(issue.location, self.location)
        
    def test_issue_string_representation(self):
        """Test the string representation of the Issue model"""
        issue = Issue.objects.create(
            title='Test Issue',
            description='This is a test issue',
            location=self.location,
            issue_type='INFRASTRUCTURE',
            reporter=self.citizen
        )
        
        self.assertEqual(str(issue), issue.title)
        
    def test_issue_default_values(self):
        """Test default values for Issue model"""
        issue = Issue.objects.create(
            title='Test Issue',
            description='This is a test issue',
            location=self.location,
            issue_type='INFRASTRUCTURE',
            reporter=self.citizen
        )
        
        self.assertEqual(issue.status, 'PENDING')  # Default status should be PENDING
        self.assertEqual(issue.priority, 'NA')  # Default priority should be NA


class IssueImageTests(TestCase):
    """Tests for the IssueImage model"""
    
    def setUp(self):
        self.citizen = User.objects.create_user(
            username='citizen',
            email='citizen@example.com',
            password='pass123',
            type='CITIZEN'
        )
        self.location = Point(78.4867, 17.3850)
        self.issue = Issue.objects.create(
            title='Test Issue',
            description='This is a test issue',
            location=self.location,
            issue_type='INFRASTRUCTURE',
            reporter=self.citizen
        )
        
        # Create a simple test image
        self.image_file = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'\x00\x01\x02\x03',  # Dummy image content
            content_type='image/jpeg'
        )
        
    def test_create_issue_image(self):
        """Test adding an image to an issue"""
        issue_image = IssueImage.objects.create(
            issue=self.issue,
            image=self.image_file,
            caption='Test image'
        )
        
        self.assertEqual(issue_image.issue, self.issue)
        self.assertEqual(issue_image.caption, 'Test image')
        self.assertTrue(issue_image.image.name.endswith('.jpg'))
        
    def test_issue_image_string_representation(self):
        """Test the string representation of IssueImage"""
        issue_image = IssueImage.objects.create(
            issue=self.issue,
            image=self.image_file,
            caption='Test image'
        )
        
        expected_str = f"Image for {self.issue.title}"
        self.assertEqual(str(issue_image), expected_str)