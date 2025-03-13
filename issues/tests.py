from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

class IssueCreationTest(APITestCase):
    def setUp(self):
        """Set up a test user and get an authentication token"""
        self.user_data = {
            "username": "vamsi",
            "password": "12345678a!",
            "type": "CITIZEN"
        }
        
        # Register the user
        self.client.post("/api/register/", self.user_data, format="json")
        
        # Get authentication token
        response = self.client.post("/api/token/", {
            "username": self.user_data["username"],
            "password": self.user_data["password"]
        }, format="json")
        
        self.token = response.data.get("access")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_create_issue(self):
        """Test creating a new issue"""
        issue_data = {
            "title": "Streetlight Not Working",
            "description": "The streetlight on Main St. is broken.",
            "location": "POINT(77.1025 28.7041)",  # Example lat/lon
            "type": "infrastructure",
        }

        response = self.client.post("/api/issues/", issue_data, format="json")

            # 🛠️ Debugging output
        print("Response Status Code:", response.status_code)
        print("Response Data:", response.data)  # This shows why it failed
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)  # Check if an issue ID is returned

class MunicipalUserTest(APITestCase):
    def setUp(self):
        """Set up a municipal user and create some issues"""
        self.municipal_user_data = {
            "username": "municipal_admin",
            "password": "StrongPass123!",
            "type": "MUNICIPAL"
        }

        self.citizen_user_data = {
            "username": "vamsi",
            "password": "12345678a!",
            "type": "CITIZEN"
        }

        # Register users
        self.client.post("/api/register/", self.municipal_user_data, format="json")
        self.client.post("/api/register/", self.citizen_user_data, format="json")

        # Get municipal user token
        response = self.client.post("/api/token/", {
            "username": self.municipal_user_data["username"],
            "password": self.municipal_user_data["password"]
        }, format="json")
        self.municipal_token = response.data.get("access")

        # Get citizen user token
        response = self.client.post("/api/token/", {
            "username": self.citizen_user_data["username"],
            "password": self.citizen_user_data["password"]
        }, format="json")
        self.citizen_token = response.data.get("access")

        # Authenticate as citizen and create issues
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.citizen_token}")
        for i in range(5):  # Create 5 issues
            self.client.post("/api/issues/", {
                "title": f"Issue {i+1}",
                "description": f"Description for issue {i+1}",
                "location": "POINT(77.1025 28.7041)"
            }, format="json")

    def test_municipal_user_can_view_issues(self):
        """Test that a municipal user can view the list of reported issues"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.municipal_token}")
        response = self.client.get("/municipal/issues/", format="json")

        print("Response Status Code:", response.status_code)
        print("Response Data:", response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)  # Ensure paginated response
        self.assertGreaterEqual(len(response.data["results"]), 5)  # At least 5 issues exist
