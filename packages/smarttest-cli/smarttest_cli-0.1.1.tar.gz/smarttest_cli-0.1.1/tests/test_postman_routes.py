import unittest
from unittest.mock import patch, MagicMock
import json
import io
from fastapi.testclient import TestClient
from fastapi import UploadFile

from main import app
from database.database import SessionLocal
from service import ClerkAuthService


class TestPostmanRoutes(unittest.TestCase):
    """Integration tests for Postman collection import API routes."""
    
    def setUp(self):
        """Set up test client and mock authentication."""
        self.client = TestClient(app)
        
        # Mock customer object for auth
        self.mock_customer = MagicMock()
        self.mock_customer.id = "test-customer-123"
        
        # Sample Postman collection for testing
        self.sample_collection = {
            "info": {
                "name": "Test API",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "variable": [
                {"key": "baseUrl", "value": "https://api.test.com"}
            ],
            "item": [
                {
                    "name": "Get Users",
                    "request": {
                        "method": "GET",
                        "url": "{{baseUrl}}/users"
                    }
                },
                {
                    "name": "Create User",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"}
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": '{"name": "John Doe", "email": "john@example.com"}'
                        },
                        "url": "{{baseUrl}}/users"
                    }
                }
            ]
        }
        
        # Sample environment
        self.sample_environment = {
            "name": "Test Environment",
            "values": [
                {"key": "baseUrl", "value": "https://test-api.example.com"},
                {"key": "apiKey", "value": "test-key-123"}
            ]
        }
        
        # Mock subscription service to allow system creation
        self.mock_usage_limits = MagicMock()
        self.mock_usage_limits.systems_used = 1
        self.mock_usage_limits.systems_limit = 10
        self.mock_usage_limits.systems_remaining = 9

    def _create_test_file(self, content: dict) -> io.BytesIO:
        """Create a test file with JSON content."""
        json_content = json.dumps(content)
        return io.BytesIO(json_content.encode('utf-8'))

    @patch('routes.system_routes._require_client_or_admin_dynamic')
    def test_postman_preview_success(self, mock_auth):
        """Test successful Postman collection preview."""
        mock_auth.return_value = self.mock_customer
        
        # Create test file
        test_file = self._create_test_file(self.sample_collection)
        
        response = self.client.post(
            "/system/postman-preview",
            files={"file": ("test.json", test_file, "application/json")}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify response structure
        self.assertIn("collection_info", data)
        self.assertIn("total_requests", data)
        self.assertIn("estimated_endpoints", data)
        self.assertIn("variables", data)
        
        # Verify collection info
        self.assertEqual(data["collection_info"]["name"], "Test API")
        self.assertEqual(data["total_requests"], 2)
        self.assertEqual(data["estimated_endpoints"], 2)
        
        # Verify variables
        self.assertIn("baseUrl", data["variables"])
        self.assertEqual(data["variables"]["baseUrl"], "https://api.test.com")

    @patch('routes.system_routes._require_client_or_admin_dynamic')
    def test_postman_preview_invalid_file(self, mock_auth):
        """Test preview with invalid file format."""
        mock_auth.return_value = self.mock_customer
        
        # Test non-JSON file
        response = self.client.post(
            "/system/postman-preview",
            files={"file": ("test.txt", io.BytesIO(b"not json"), "text/plain")}
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid file format", response.json()["detail"])

    @patch('routes.system_routes._require_client_or_admin_dynamic')
    def test_postman_preview_invalid_collection(self, mock_auth):
        """Test preview with invalid collection format."""
        mock_auth.return_value = self.mock_customer
        
        invalid_collection = {
            "info": {
                "name": "Invalid Collection"
                # Missing schema
            },
            "item": []
        }
        
        test_file = self._create_test_file(invalid_collection)
        
        response = self.client.post(
            "/system/postman-preview",
            files={"file": ("test.json", test_file, "application/json")}
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid Postman collection format", response.json()["detail"])

    @patch('service.SubscriptionService.SubscriptionService.increment_usage')
    @patch('service.CustomerService.create_system_access')
    @patch('service.SubscriptionService.SubscriptionService.get_usage_limits')
    @patch('service.SubscriptionService.SubscriptionService.can_create_system')
    @patch('routes.system_routes._require_client_or_admin_dynamic')
    def test_postman_import_success(self, mock_auth, mock_can_create, mock_get_limits, 
                                  mock_create_access, mock_increment):
        """Test successful Postman collection import."""
        mock_auth.return_value = self.mock_customer
        mock_can_create.return_value = True
        mock_get_limits.return_value = self.mock_usage_limits
        
        # Create test file
        test_file = self._create_test_file(self.sample_collection)
        
        response = self.client.post(
            "/system/postman-import",
            files={"file": ("test.json", test_file, "application/json")},
            data={"name": "Imported API"}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify response structure
        self.assertIn("system_id", data)
        self.assertIn("name", data)
        self.assertIn("successful_endpoints", data)
        self.assertIn("import_summary", data)
        
        # Verify system creation
        self.assertEqual(data["name"], "Imported API")
        self.assertEqual(len(data["successful_endpoints"]), 2)
        
        # Verify import summary
        summary = data["import_summary"]
        self.assertEqual(summary["total"], 2)
        self.assertEqual(summary["successful"], 2)
        self.assertEqual(summary["failed"], 0)
        
        # Verify that system access was created
        mock_create_access.assert_called_once()
        
        # Verify usage tracking
        mock_increment.assert_called_with(unittest.mock.ANY, self.mock_customer.id, "systems_created")

    @patch('service.SubscriptionService.SubscriptionService.can_create_system')
    @patch('routes.system_routes._require_client_or_admin_dynamic')
    def test_postman_import_subscription_limit(self, mock_auth, mock_can_create):
        """Test import failure due to subscription limits."""
        mock_auth.return_value = self.mock_customer
        mock_can_create.return_value = False
        
        # Mock limits for error message
        with patch('service.SubscriptionService.SubscriptionService.get_usage_limits') as mock_get_limits:
            mock_limits = MagicMock()
            mock_limits.systems_used = 10
            mock_limits.systems_limit = 10
            mock_get_limits.return_value = mock_limits
            
            test_file = self._create_test_file(self.sample_collection)
            
            response = self.client.post(
                "/system/postman-import",
                files={"file": ("test.json", test_file, "application/json")},
                data={"name": "Test Import"}
            )
            
            self.assertEqual(response.status_code, 403)
            self.assertIn("System creation limit reached", response.json()["detail"])

    @patch('service.SubscriptionService.SubscriptionService.increment_usage')
    @patch('service.CustomerService.create_system_access') 
    @patch('service.SubscriptionService.SubscriptionService.get_usage_limits')
    @patch('service.SubscriptionService.SubscriptionService.can_create_system')
    @patch('routes.system_routes._require_client_or_admin_dynamic')
    def test_postman_import_with_environment(self, mock_auth, mock_can_create, mock_get_limits,
                                          mock_create_access, mock_increment):
        """Test import with environment selection."""
        mock_auth.return_value = self.mock_customer
        mock_can_create.return_value = True
        mock_get_limits.return_value = self.mock_usage_limits
        
        test_file = self._create_test_file(self.sample_collection)
        
        response = self.client.post(
            "/system/postman-import",
            files={"file": ("test.json", test_file, "application/json")},
            data={
                "name": "API with Environment",
                "environment_data": json.dumps(self.sample_environment)
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should still create system successfully
        self.assertIn("system_id", data)
        self.assertEqual(data["name"], "API with Environment")
        self.assertEqual(len(data["successful_endpoints"]), 2)

    @patch('service.SubscriptionService.SubscriptionService.can_create_system')
    @patch('routes.system_routes._require_client_or_admin_dynamic')
    def test_postman_import_invalid_file(self, mock_auth, mock_can_create):
        """Test import with invalid file format."""
        mock_auth.return_value = self.mock_customer
        mock_can_create.return_value = True
        
        response = self.client.post(
            "/system/postman-import",
            files={"file": ("test.txt", io.BytesIO(b"not json"), "text/plain")},
            data={"name": "Test Import"}
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid file format", response.json()["detail"])

    @patch('service.SubscriptionService.SubscriptionService.can_create_system')
    @patch('routes.system_routes._require_client_or_admin_dynamic')
    def test_postman_import_invalid_json(self, mock_auth, mock_can_create):
        """Test import with invalid JSON content."""
        mock_auth.return_value = self.mock_customer
        mock_can_create.return_value = True
        
        response = self.client.post(
            "/system/postman-import",
            files={"file": ("test.json", io.BytesIO(b"{invalid json}"), "application/json")},
            data={"name": "Test Import"}
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("Error processing file", response.json()["detail"])

    @patch('service.SubscriptionService.SubscriptionService.can_create_system')
    @patch('routes.system_routes._require_client_or_admin_dynamic')
    def test_postman_import_invalid_environment(self, mock_auth, mock_can_create):
        """Test import with invalid environment data."""
        mock_auth.return_value = self.mock_customer
        mock_can_create.return_value = True
        
        test_file = self._create_test_file(self.sample_collection)
        
        response = self.client.post(
            "/system/postman-import", 
            files={"file": ("test.json", test_file, "application/json")},
            data={
                "name": "Test Import",
                "environment_data": "{invalid json}"
            }
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid environment data format", response.json()["detail"])

    @patch('service.SubscriptionService.SubscriptionService.can_create_system')
    @patch('routes.system_routes._require_client_or_admin_dynamic')
    def test_postman_import_empty_collection(self, mock_auth, mock_can_create):
        """Test import with collection containing no valid endpoints."""
        mock_auth.return_value = self.mock_customer
        mock_can_create.return_value = True
        
        empty_collection = {
            "info": {
                "name": "Empty Collection",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": []
        }
        
        test_file = self._create_test_file(empty_collection)
        
        response = self.client.post(
            "/system/postman-import",
            files={"file": ("test.json", test_file, "application/json")},
            data={"name": "Empty Import"}
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("No valid endpoints found", response.json()["detail"])

    def test_count_requests_helper_function(self):
        """Test the helper function that counts requests in collection items."""
        from routes.system_routes import _count_requests_in_items
        
        # Test simple items
        simple_items = [
            {"name": "Request 1", "request": {"method": "GET", "url": "test"}},
            {"name": "Request 2", "request": {"method": "POST", "url": "test"}}
        ]
        self.assertEqual(_count_requests_in_items(simple_items), 2)
        
        # Test nested folders
        nested_items = [
            {"name": "Request 1", "request": {"method": "GET", "url": "test"}},
            {
                "name": "Folder 1",
                "item": [
                    {"name": "Request 2", "request": {"method": "POST", "url": "test"}},
                    {"name": "Request 3", "request": {"method": "PUT", "url": "test"}}
                ]
            }
        ]
        self.assertEqual(_count_requests_in_items(nested_items), 3)
        
        # Test items without requests (should be ignored)
        mixed_items = [
            {"name": "Request 1", "request": {"method": "GET", "url": "test"}},
            {"name": "Invalid Item"},  # No request key
            {"name": "Request 2", "request": {"method": "POST", "url": "test"}}
        ]
        self.assertEqual(_count_requests_in_items(mixed_items), 2)


if __name__ == "__main__":
    unittest.main()