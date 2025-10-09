import unittest
from unittest.mock import patch, MagicMock
import json
from fastapi.testclient import TestClient
from fastapi import HTTPException

from main import app
from database.schemas import ScenarioCreateRequest
from database.model import ScenarioDB, EndpointDB
from service.ScenarioService import create_manual_scenario
from service.AuthService import require_auth


class TestManualScenarioCreation(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.endpoint_id = 1
        self.scenario_data = {
            "name": "Test Manual Scenario",
            "requires_auth": False
        }

    def test_scenario_create_request_schema(self):
        """Test ScenarioCreateRequest schema validation"""
        # Valid data
        valid_request = ScenarioCreateRequest(
            name="Test Scenario",
            requires_auth=True
        )
        self.assertEqual(valid_request.name, "Test Scenario")
        self.assertEqual(valid_request.requires_auth, True)
        
        # Default requires_auth
        default_request = ScenarioCreateRequest(name="Test Scenario 2")
        self.assertEqual(default_request.requires_auth, False)
        
        # Invalid - missing name
        with self.assertRaises(Exception):
            ScenarioCreateRequest(requires_auth=True)

    def test_scenario_creation_logic(self):
        """Test manual scenario creation business logic"""
        request = ScenarioCreateRequest(
            name="Business Logic Test",
            requires_auth=True
        )
        
        # Test that request properly maps to scenario creation
        self.assertEqual(request.name, "Business Logic Test")
        self.assertEqual(request.requires_auth, True)

    def test_create_manual_scenario_service(self):
        """Test create_manual_scenario service method"""
        # Setup mock session
        mock_session = MagicMock()
        
        # Create test request
        scenario_request = ScenarioCreateRequest(
            name="Test Service Scenario",
            requires_auth=True
        )
        
        result = create_manual_scenario(mock_session, 5, scenario_request)
        
        # Verify session.add was called with ScenarioDB
        mock_session.add.assert_called_once()
        created_scenario_db = mock_session.add.call_args[0][0]
        
        # Verify all the values are set correctly
        self.assertEqual(created_scenario_db.endpoint_id, 5)
        self.assertEqual(created_scenario_db.name, "Test Service Scenario")
        self.assertEqual(created_scenario_db.requires_auth, True)
        self.assertEqual(created_scenario_db.expected_http_status, 200)
        self.assertEqual(created_scenario_db.llm_validation_status, 'pending')
        self.assertIsNone(created_scenario_db.error_in)
        
        # Verify the result is the same object
        self.assertEqual(result, created_scenario_db)

    def test_scenario_default_values(self):
        """Test that manual scenarios are created with correct defaults"""
        mock_session = MagicMock()
        scenario_request = ScenarioCreateRequest(
            name="Default Values Test",
            requires_auth=False
        )
        
        result = create_manual_scenario(mock_session, 5, scenario_request)
        
        # Verify session.add was called
        mock_session.add.assert_called_once()
        created_scenario_db = mock_session.add.call_args[0][0]  # First argument to session.add
        
        # Check all the default values
        self.assertEqual(created_scenario_db.endpoint_id, 5)
        self.assertEqual(created_scenario_db.name, "Default Values Test")
        self.assertEqual(created_scenario_db.requires_auth, False)
        self.assertEqual(created_scenario_db.expected_http_status, 200)
        self.assertEqual(created_scenario_db.llm_validation_status, 'pending')
        self.assertIsNone(created_scenario_db.error_in)
        self.assertIsNone(created_scenario_db.error_type)
        self.assertIsNone(created_scenario_db.error_attribute)
        self.assertIsNone(created_scenario_db.error_description)
        self.assertEqual(created_scenario_db.auth_error, False)
        
        # Verify the scenario DB object was returned
        self.assertEqual(result, created_scenario_db)


class TestManualScenarioCreationSecurity(unittest.TestCase):
    """Test security and validation aspects of manual scenario creation"""
    
    def setUp(self):
        self.client = TestClient(app)
        self.endpoint_id = 123
        self.valid_scenario_data = {
            "name": "Test Security Scenario", 
            "requires_auth": False
        }
    
    def _create_mock_customer(self, customer_id="user123"):
        """Helper to create a mock customer"""
        mock_customer = MagicMock()
        mock_customer.id = customer_id
        mock_customer.email = "test@example.com"
        return mock_customer
    
    def test_scenario_creation_requires_authentication(self):
        """Test that scenario creation fails without authentication"""
        # Make request without auth token
        response = self.client.post(
            f"/endpoints/{self.endpoint_id}/scenarios",
            json=self.valid_scenario_data
        )
        
        # Should return 401 Unauthorized
        self.assertEqual(response.status_code, 401)
        response_data = response.json()
        self.assertIn("Authentication required", response_data["detail"])
    
    @patch('routes.endpoint_routes.SubscriptionService.can_create_scenario')
    @patch('routes.endpoint_routes.SubscriptionService.get_usage_limits')
    def test_scenario_creation_subscription_limits(self, mock_get_limits, mock_can_create):
        """Test that scenario creation respects subscription tier limits"""
        # Override auth dependency
        mock_customer = self._create_mock_customer()
        app.dependency_overrides[require_auth] = lambda: mock_customer
        
        # Mock subscription limit reached
        mock_can_create.return_value = False
        mock_limits = MagicMock()
        mock_limits.scenarios_used = 10
        mock_limits.scenarios_limit = 10
        mock_get_limits.return_value = mock_limits
        
        # Make request
        response = self.client.post(
            f"/endpoints/{self.endpoint_id}/scenarios",
            json=self.valid_scenario_data
        )
        
        # Should return 403 Forbidden with limit message
        self.assertEqual(response.status_code, 403)
        response_data = response.json()
        self.assertIn("Scenario creation limit reached", response_data["detail"])
        self.assertIn("10/10 scenarios", response_data["detail"])
        self.assertIn("upgrade your plan", response_data["detail"])
        
        # Verify the limit check was called
        mock_can_create.assert_called_once_with(unittest.mock.ANY, "user123")
        mock_get_limits.assert_called_once_with(unittest.mock.ANY, "user123")
        
        # Clean up
        app.dependency_overrides.clear()
    
    @patch('routes.endpoint_routes.SubscriptionService.can_create_scenario')
    @patch('routes.endpoint_routes.check_endpoint_exists')
    @patch('routes.endpoint_routes.CustomerService.check_user_system_access')
    def test_scenario_creation_system_access_control(self, mock_check_access, mock_check_endpoint, mock_can_create):
        """Test that users can only create scenarios in systems they have access to"""
        # Override auth dependency
        mock_customer = self._create_mock_customer()
        app.dependency_overrides[require_auth] = lambda: mock_customer
        
        mock_can_create.return_value = True
        
        mock_endpoint = MagicMock()
        mock_endpoint.system_id = 4  # Match the actual system_id from logs
        mock_check_endpoint.return_value = mock_endpoint
        
        # Mock access denied
        mock_check_access.side_effect = HTTPException(status_code=403, detail="Access denied to system")
        
        # Make request
        response = self.client.post(
            f"/endpoints/{self.endpoint_id}/scenarios",
            json=self.valid_scenario_data
        )
        
        # Should return 403 Forbidden
        self.assertEqual(response.status_code, 403)
        response_data = response.json()
        self.assertEqual(response_data["detail"], "Access denied to system")
        
        # Verify access check was called with correct parameters
        mock_check_access.assert_called_once_with(unittest.mock.ANY, "user123", 4)
        
        # Clean up
        app.dependency_overrides.clear()
    
    @patch('routes.endpoint_routes.SubscriptionService.can_create_scenario')
    @patch('routes.endpoint_routes.check_endpoint_exists')
    @patch('routes.endpoint_routes.CustomerService.check_user_system_access')  
    def test_scenario_creation_endpoint_not_found(self, mock_check_access, mock_check_endpoint, mock_can_create):
        """Test that scenario creation fails if endpoint doesn't exist"""
        # Override auth dependency
        mock_customer = self._create_mock_customer()
        app.dependency_overrides[require_auth] = lambda: mock_customer
        
        mock_can_create.return_value = True  # Allow subscription check to pass first
        
        # Mock endpoint not found (this should be called before access check)
        mock_check_endpoint.side_effect = HTTPException(status_code=404, detail="Endpoint with id 123 not found")
        
        # Mock access check to pass if reached (but shouldn't be reached due to endpoint not found)
        mock_check_access.return_value = None
        
        # Make request
        response = self.client.post(
            f"/endpoints/{self.endpoint_id}/scenarios",
            json=self.valid_scenario_data
        )
        
        # Should return 404 Not Found
        self.assertEqual(response.status_code, 404)
        response_data = response.json()
        self.assertEqual(response_data["detail"], "Endpoint with id 123 not found")
        
        # Clean up
        app.dependency_overrides.clear()
    
    def test_scenario_creation_input_validation_missing_name(self):
        """Test that scenario creation fails without a name"""
        # Override auth dependency
        mock_customer = self._create_mock_customer()
        app.dependency_overrides[require_auth] = lambda: mock_customer
        
        invalid_data = {"requires_auth": False}  # Missing name
        
        # Make request with mock auth token
        response = self.client.post(
            f"/endpoints/{self.endpoint_id}/scenarios",
            json=invalid_data,
            headers={"Authorization": "Bearer mock_token"}
        )
        
        # Should return 422 Unprocessable Entity for validation error
        self.assertEqual(response.status_code, 422)
        response_data = response.json()
        self.assertIn("detail", response_data)
        
        # Check that the error mentions the missing name field
        validation_errors = response_data["detail"]
        self.assertTrue(any("name" in str(error) for error in validation_errors))
        
        # Clean up
        app.dependency_overrides.clear()
    
    def test_scenario_creation_input_validation_empty_name(self):
        """Test that scenario creation fails with empty name"""
        # Override auth dependency
        mock_customer = self._create_mock_customer()
        app.dependency_overrides[require_auth] = lambda: mock_customer
        
        invalid_data = {"name": "", "requires_auth": False}  # Empty name
        
        response = self.client.post(
            f"/endpoints/{self.endpoint_id}/scenarios",
            json=invalid_data,
            headers={"Authorization": "Bearer mock_token"}
        )
        
        # Should return 422 for empty string validation
        self.assertEqual(response.status_code, 422)
        
        # Clean up
        app.dependency_overrides.clear()
    
    @patch('routes.endpoint_routes.SubscriptionService.can_create_scenario')
    @patch('routes.endpoint_routes.check_endpoint_exists')
    @patch('routes.endpoint_routes.CustomerService.check_user_system_access')
    @patch('service.ScenarioService.create_manual_scenario')
    @patch('routes.endpoint_routes.SubscriptionService.increment_usage')
    def test_successful_scenario_creation_with_security_checks(
        self, mock_increment, mock_create_scenario, mock_check_access, 
        mock_check_endpoint, mock_can_create
    ):
        """Test successful scenario creation when all security checks pass"""
        # Override auth dependency
        mock_customer = self._create_mock_customer()
        app.dependency_overrides[require_auth] = lambda: mock_customer
        
        mock_can_create.return_value = True
        
        mock_endpoint = MagicMock()
        mock_endpoint.system_id = 1
        mock_check_endpoint.return_value = mock_endpoint
        
        mock_check_access.return_value = None  # No exception = access granted
        
        # Create a proper ScenarioDB object (not a mock) to avoid Pydantic validation issues
        from database.model import ScenarioDB
        mock_scenario_db = ScenarioDB(
            id=999,
            endpoint_id=self.endpoint_id,
            name=self.valid_scenario_data["name"],
            expected_http_status=200,
            error_in=None,
            error_type=None,
            error_attribute=None,
            error_description=None,
            requires_auth=self.valid_scenario_data["requires_auth"],
            auth_error=False,
            llm_validation_status='pending',
            llm_last_validated_at=None,
            llm_validation_result=None
        )
        mock_create_scenario.return_value = mock_scenario_db
        
        # Make request
        response = self.client.post(
            f"/endpoints/{self.endpoint_id}/scenarios",
            json=self.valid_scenario_data
        )
        
        # Should succeed
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data["success"])
        self.assertEqual(response_data["message"], f"Scenario '{self.valid_scenario_data['name']}' created successfully")
        
        # Verify all security checks were called in correct order
        mock_can_create.assert_called_once_with(unittest.mock.ANY, "user123")
        mock_check_endpoint.assert_called_once_with(unittest.mock.ANY, self.endpoint_id)
        mock_check_access.assert_called_once_with(unittest.mock.ANY, "user123", 1)
        mock_create_scenario.assert_called_once()
        mock_increment.assert_called_once_with(unittest.mock.ANY, "user123", "scenarios_created", 1)
        
        # Clean up
        app.dependency_overrides.clear()


if __name__ == "__main__":
    unittest.main()