from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from issues.models import Issue, IssueImage

User = get_user_model()

class AuthorizationSecurityTests(TestCase):
    """Tests for proper authorization and access control for issues"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create users with different roles
        self.citizen1 = User.objects.create_user(
            username='citizen1',
            email='citizen1@example.com',
            password='Pass123!',
            type='CITIZEN'
        )
        
        self.citizen2 = User.objects.create_user(
            username='citizen2',
            email='citizen2@example.com',
            password='Pass123!',
            type='CITIZEN'
        )
        
        self.municipal = User.objects.create_user(
            username='municipal',
            email='municipal@example.com',
            password='Pass123!',
            type='MUNICIPAL'
        )
        
        # Create issues for different users
        self.location = Point(78.4867, 17.3850)
        
        self.citizen1_issue = Issue.objects.create(
            title='Citizen 1 Issue',
            description='This is citizen 1\'s issue',
            location=self.location,
            issue_type='INFRASTRUCTURE',
            reporter=self.citizen1
        )
        
        self.citizen2_issue = Issue.objects.create(
            title='Citizen 2 Issue',
            description='This is citizen 2\'s issue',
            location=self.location,
            issue_type='SERVICES',
            reporter=self.citizen2
        )
        
        # Set up URLs
        self.citizen1_issue_url = reverse('issue-detail', args=[self.citizen1_issue.id])
        self.citizen2_issue_url = reverse('issue-detail', args=[self.citizen2_issue.id])
        self.issues_url = reverse('issue-list')
        
    def test_citizen_access_own_issue(self):
        """Test citizens can access their own issues"""
        self.client.force_authenticate(user=self.citizen1)
        
        response = self.client.get(self.citizen1_issue_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.citizen1_issue.title)
        
    def test_citizen_cannot_access_others_issue(self):
        """Test citizens cannot access others' issues"""
        self.client.force_authenticate(user=self.citizen1)
        
        response = self.client.get(self.citizen2_issue_url)
        
        # Depending on your implementation - could be 403 Forbidden or 404 Not Found
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])
        
    def test_municipal_can_access_all_issues(self):
        """Test municipal users can access all issues"""
        self.client.force_authenticate(user=self.municipal)
        
        response1 = self.client.get(self.citizen1_issue_url)
        response2 = self.client.get(self.citizen2_issue_url)
        
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
    def test_citizen_cannot_update_others_issue(self):
        """Test citizens cannot update others' issues"""
        self.client.force_authenticate(user=self.citizen1)
        
        payload = {
            'description': 'Unauthorized update'
        }
        
        response = self.client.patch(self.citizen2_issue_url, payload)
        
        # Depending on your implementation - could be 403 Forbidden or 404 Not Found
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])
        
    def test_citizen_cannot_delete_issues(self):
        """Test citizens cannot delete issues (even their own, if that's your policy)"""
        self.client.force_authenticate(user=self.citizen1)
        
        response = self.client.delete(self.citizen1_issue_url)
        
        # If citizens aren't allowed to delete issues
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_municipal_can_update_any_issue(self):
        """Test municipal users can update any issue"""
        self.client.force_authenticate(user=self.municipal)
        
        payload = {
            'status': 'IN PROGRESS',
            'priority': 'HIGH'
        }
        
        response = self.client.patch(self.citizen1_issue_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.citizen1_issue.refresh_from_db()
        self.assertEqual(self.citizen1_issue.status, 'IN PROGRESS')
        self.assertEqual(self.citizen1_issue.priority, 'HIGH')
        
    def test_citizen_cannot_bypass_role_restrictions(self):
        """Test citizens cannot perform actions reserved for municipal users by manipulating requests"""
        self.client.force_authenticate(user=self.citizen1)
        
        # Try to update status and priority (assuming these are municipal-only fields)
        payload = {
            'status': 'RESOLVED',
            'priority': 'HIGH'
        }
        
        response = self.client.patch(self.citizen1_issue_url, payload)
        
        # The implementation should either return 403 or silently ignore the restricted fields
        self.citizen1_issue.refresh_from_db()
        self.assertNotEqual(self.citizen1_issue.status, 'RESOLVED')


class DataValidationSecurityTests(TestCase):
    """Tests for input validation and sanitization for issues"""
    
    def setUp(self):
        self.client = APIClient()
        self.issues_url = reverse('issue-list')
        
        # Create a citizen user
        self.citizen = User.objects.create_user(
            username='citizen',
            email='citizen@example.com',
            password='Pass123!',
            type='CITIZEN'
        )
        
        self.location = Point(78.4867, 17.3850)
        
    def test_xss_prevention(self):
        """Test prevention of XSS attacks in text fields"""
        self.client.force_authenticate(user=self.citizen)
        
        # Create issue with potential XSS payload
        xss_payload = '<script>alert("XSS")</script>'
        
        payload = {
            'title': f'Test Issue {xss_payload}',
            'description': f'Description {xss_payload}',
            'location': {'type': 'Point', 'coordinates': [78.4867, 17.3850]},
            'issue_type': 'INFRASTRUCTURE',
        }
        
        response = self.client.post(self.issues_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Get the issue and check if XSS is sanitized/escaped
        issue_id = response.data['id']
        issue_url = reverse('issue-detail', args=[issue_id])
        
        response = self.client.get(issue_url)
        
        # The exact behavior depends on your sanitization strategy
        # At minimum, the raw script tag should not be present as-is
        self.assertNotIn('<script>alert("XSS")</script>', response.data['title'])
        self.assertNotIn('<script>alert("XSS")</script>', response.data['description'])
        
    def test_invalid_location_data_rejection(self):
        """Test system rejects invalid location data"""
        self.client.force_authenticate(user=self.citizen)
        
        invalid_locations = [
            {'type': 'Point', 'coordinates': [200, 200]},  # Invalid coordinates
            {'type': 'LineString', 'coordinates': [[0, 0], [1, 1]]},  # Wrong geometry type
            {'type': 'Invalid', 'coordinates': [78, 17]},  # Invalid type
            {'coordinates': [78, 17]},  # Missing type
            {'type': 'Point'}  # Missing coordinates
        ]
        
        for location in invalid_locations:
            payload = {
                'title': 'Test Issue',
                'description': 'This is a test issue',
                'location': location,
                'issue_type': 'INFRASTRUCTURE',
            }
            
            response = self.client.post(self.issues_url, payload, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ContentSecurityTests(TestCase):
    """Tests for content security policy and upload handling"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create a user
        self.citizen = User.objects.create_user(
            username='citizen',
            email='citizen@example.com',
            password='Pass123!',
            type='CITIZEN'
        )
        
        self.location = Point(78.4867, 17.3850)
        
        # Create an issue
        self.issue = Issue.objects.create(
            title='Test Issue',
            description='This is a test issue',
            location=self.location,
            issue_type='INFRASTRUCTURE',
            reporter=self.citizen
        )
        
        self.add_image_url = reverse('issue-add-image', args=[self.issue.id])
        
    def test_malicious_file_upload_prevention(self):
        """Test prevention of malicious file uploads"""
        self.client.force_authenticate(user=self.citizen)
        
        # Create a fake executable disguised as an image
        malicious_file = SimpleUploadedFile(
            name='malicious.jpg',
            content=b'#!/bin/bash\necho "This is not an image"',
            content_type='image/jpeg'
        )
        
        response = self.client.post(
            self.add_image_url, 
            {'image': malicious_file, 'caption': 'Test Image'},
            format='multipart'
        )
        
        # The server should reject this file as it's not actually an image
        # The exact behavior depends on your validation strategy
        self.assertIn(response.status_code, 
                     [status.HTTP_400_BAD_REQUEST, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE])
        
    def test_oversized_file_rejection(self):
        """Test rejection of oversized file uploads"""
        self.client.force_authenticate(user=self.citizen)
        
        # Create a large file that exceeds your size limit
        # This test assumes you have a reasonable file size limit
        large_content = b'\x00' * (10 * 1024 * 1024)  # 10MB file
        large_file = SimpleUploadedFile(
            name='large_image.jpg',
            content=large_content,
            content_type='image/jpeg'
        )
        
        response = self.client.post(
            self.add_image_url, 
            {'image': large_file, 'caption': 'Large Image'},
            format='multipart'
        )
        
        # The server should reject this file as it's too large
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)