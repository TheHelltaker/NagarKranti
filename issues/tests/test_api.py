from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from issues.models import Issue, IssueImage

User = get_user_model()

class IssueAPITests(TestCase):
    """Tests for the issue API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.issues_url = reverse('issue-list')
        
        # Create users
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
        
        # Create a test issue
        self.issue = Issue.objects.create(
            title='Test Issue',
            description='This is a test issue',
            location=self.location,
            issue_type='INFRASTRUCTURE',
            status='PENDING',
            priority='NORMAL',
            reporter=self.citizen
        )
        
        self.issue_detail_url = reverse('issue-detail', args=[self.issue.id])
        self.nearby_url = reverse('issue-nearby')
        
    def test_create_issue_as_citizen(self):
        """Test creating an issue as a citizen"""
        self.client.force_authenticate(user=self.citizen)
        
        payload = {
            'title': 'New Issue',
            'description': 'This is a new issue',
            'location': {'type': 'Point', 'coordinates': [78.4867, 17.3850]},
            'issue_type': 'SERVICES',
        }
        
        response = self.client.post(self.issues_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        issue = Issue.objects.get(title='New Issue')
        self.assertEqual(issue.reporter, self.citizen)
        self.assertEqual(issue.status, 'PENDING')  # Default status
        
    def test_create_issue_as_municipal(self):
        """Test creating an issue as a municipal user (should be allowed)"""
        self.client.force_authenticate(user=self.municipal)
        
        payload = {
            'title': 'Municipal Issue',
            'description': 'This is an issue reported by municipal staff',
            'location': {'type': 'Point', 'coordinates': [78.4867, 17.3850]},
            'issue_type': 'INFRASTRUCTURE',
        }
        
        response = self.client.post(self.issues_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_update_issue_as_citizen_own_issue(self):
        """Test citizen updating their own issue"""
        self.client.force_authenticate(user=self.citizen)
        
        payload = {
            'description': 'Updated description',
        }
        
        response = self.client.patch(self.issue_detail_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.issue.refresh_from_db()
        self.assertEqual(self.issue.description, 'Updated description')
        
    def test_citizen_cannot_update_status(self):
        """Test citizens cannot update issue status"""
        self.client.force_authenticate(user=self.citizen)
        
        payload = {
            'status': 'RESOLVED',
        }
        
        response = self.client.patch(self.issue_detail_url, payload)
        
        # Check response (implementation might vary - could be forbidden or ignored)
        # Here we assume the API ignores the restricted field
        self.issue.refresh_from_db()
        self.assertNotEqual(self.issue.status, 'RESOLVED')
        
    def test_municipal_can_update_status(self):
        """Test municipal users can update issue status"""
        self.client.force_authenticate(user=self.municipal)
        
        payload = {
            'status': 'IN PROGRESS',
            'priority': 'HIGH',
        }
        
        response = self.client.patch(self.issue_detail_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.issue.refresh_from_db()
        self.assertEqual(self.issue.status, 'IN PROGRESS')
        self.assertEqual(self.issue.priority, 'HIGH')
        
    def test_list_issues_as_citizen(self):
        """Test citizens can only see their own issues"""
        self.client.force_authenticate(user=self.citizen)
        
        response = self.client.get(self.issues_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Should only see own issue
        
    def test_list_issues_as_municipal(self):
        """Test municipal users can see all issues"""
        self.client.force_authenticate(user=self.municipal)
        
        # Create another issue by another citizen
        other_citizen = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='pass123',
            type='CITIZEN'
        )
        
        Issue.objects.create(
            title='Other Issue',
            description='This is another issue',
            location=self.location,
            issue_type='SERVICES',
            reporter=other_citizen
        )
        
        response = self.client.get(self.issues_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Should see all issues
        
    def test_nearby_issues(self):
        """Test finding nearby issues"""
        self.client.force_authenticate(user=self.municipal)
        
        # Create a distant issue
        distant_location = Point(77.2090, 28.6139)  # Delhi coordinates (far from Hyderabad)
        Issue.objects.create(
            title='Distant Issue',
            description='This is a distant issue',
            location=distant_location,
            issue_type='INFRASTRUCTURE',
            reporter=self.citizen
        )
        
        # Create a nearby issue
        nearby_location = Point(78.4880, 17.3860)  # Very close to original location
        Issue.objects.create(
            title='Nearby Issue',
            description='This is a nearby issue',
            location=nearby_location,
            issue_type='INFRASTRUCTURE',
            reporter=self.citizen
        )
        
        # Request nearby issues (within 1km)
        params = {
            'lat': 78.4867, 
            'lng': 17.3850,
            'distance': 1  # 1km
        }
        
        response = self.client.get(self.nearby_url, params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return the original issue and the nearby one, but not the distant one
        self.assertEqual(len(response.data), 2)


class IssueImageAPITests(TestCase):
    """Tests for the issue image API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create users
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
        
        self.location = Point(78.4867, 17.3850)
        
        # Create a test issue
        self.issue = Issue.objects.create(
            title='Test Issue',
            description='This is a test issue',
            location=self.location,
            issue_type='INFRASTRUCTURE',
            reporter=self.citizen
        )
        
        self.add_image_url = reverse('issue-add-image', args=[self.issue.id])
        
        # Create a simple test image
        self.image_file = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'\x00\x01\x02\x03',  # Dummy image content
            content_type='image/jpeg'
        )
        
    def test_add_image_to_issue(self):
        """Test adding an image to an issue"""
        self.client.force_authenticate(user=self.citizen)
        
        response = self.client.post(
            self.add_image_url, 
            {'image': self.image_file, 'caption': 'Test Image'},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(IssueImage.objects.count(), 1)
        self.assertEqual(IssueImage.objects.first().issue, self.issue)
        
    def test_municipal_add_image(self):
        """Test municipal users can add images to issues"""
        self.client.force_authenticate(user=self.municipal)
        
        response = self.client.post(
            self.add_image_url, 
            {'image': self.image_file, 'caption': 'Municipal Image'},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_unauthorized_add_image(self):
        """Test unauthenticated users cannot add images"""
        response = self.client.post(
            self.add_image_url, 
            {'image': self.image_file, 'caption': 'Unauthorized Image'},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)