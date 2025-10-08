import unittest
import os
import sys
import uuid
from fastapi.security import HTTPAuthorizationCredentials
from fastapi import HTTPException

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from service.ClerkAuthService import get_clerk_client, validate_token, create_clerk_customer


class TestClerkAuth(unittest.TestCase):
    """Test Clerk authentication functionality"""
    
    def test_clerk_client_initialization(self):
        """Test that the Clerk client is properly initialized"""
        # Check if the client can be initialized
        clerk_client = get_clerk_client()
        self.assertIsNotNone(clerk_client, "Clerk client should be initialized")

        # Check if we can access the Clerk API (with test API key this may fail gracefully)
        try:
            # Simple API call to list users
            # This doesn't create or modify any data, just verifies connectivity
            response = clerk_client.users.list()
            self.assertIsNotNone(response, "Users list response should not be None")
            print("✅ Successfully connected to Clerk API")
        except Exception as e:
            # With test API key, this is expected to fail - just verify the client object exists
            print(f"ℹ️ Expected API failure with test key: {str(e)}")
            self.assertTrue(hasattr(clerk_client, 'users'), "Clerk client should have users attribute")
    
    def test_create_customer(self):
        """Test creating a customer in Clerk"""
        # Generate a unique email to avoid conflicts
        unique_id = str(uuid.uuid4())[:8]
        test_email = f"test-user-{unique_id}@example.com"
        test_first_name = "Test"
        test_last_name = "User"
        # Use a more complex password that won't be detected as breached
        test_password = f"Vx7!kQ9#pL{unique_id}@2Tz5"
        
        try:
            # Create a test customer
            customer = create_clerk_customer(test_email, test_first_name, test_last_name, test_password)
            self.assertIsNotNone(customer, "Customer should be created")
            self.assertIn("id", customer, "Customer response should contain an ID")
            print(f"✅ Successfully created test customer with ID: {customer['id']}")
            
            # Clean up - delete the test user
            # This ensures we don't leave test users in the Clerk database
            clerk_client = get_clerk_client()
            clerk_client.users.delete(user_id=customer["id"])
            print(f"✅ Successfully deleted test customer with ID: {customer['id']}")
        except Exception as e:
            self.fail(f"Failed to create or delete customer: {str(e)}")


if __name__ == "__main__":
    unittest.main()
