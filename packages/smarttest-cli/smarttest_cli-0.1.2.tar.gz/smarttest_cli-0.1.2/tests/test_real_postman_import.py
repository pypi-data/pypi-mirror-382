import unittest
import json
import os
from postmanParser import PostmanParser


class TestRealPostmanImport(unittest.TestCase):
    """Test Postman import functionality with the real uberall collection."""

    def setUp(self):
        """Load the real Postman collection file."""
        collection_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                     'uberall.postman_collection.json')
        
        if not os.path.exists(collection_path):
            self.skipTest("uberall.postman_collection.json not found")
        
        with open(collection_path, 'r') as f:
            self.real_collection = json.load(f)

    def test_real_collection_validation(self):
        """Test that the real collection passes validation."""
        parser = PostmanParser(self.real_collection)
        
        # Should validate successfully
        self.assertTrue(parser.validate_collection_format())
        
        # Should extract collection info
        info = parser.extract_collection_info()
        self.assertEqual(info["name"], "uberall")
        self.assertIn("schema", info)

    def test_real_collection_endpoint_extraction(self):
        """Test endpoint extraction from real collection."""
        parser = PostmanParser(self.real_collection)
        
        # Extract endpoints
        endpoints = parser.extract_endpoints()
        
        # Should find some endpoints
        self.assertGreater(len(endpoints), 0)
        print(f"Found {len(endpoints)} endpoints in real collection")
        
        # Check first endpoint details
        first_endpoint = endpoints[0]
        self.assertIsNotNone(first_endpoint.method)
        self.assertIsNotNone(first_endpoint.endpoint)
        self.assertIsNotNone(first_endpoint.raw_definition)
        
        print(f"First endpoint: {first_endpoint.method} {first_endpoint.endpoint}")

    def test_real_collection_base_url_extraction(self):
        """Test base URL extraction from real collection."""
        parser = PostmanParser(self.real_collection)
        
        base_url = parser.extract_base_url()
        
        # Should extract some base URL (might be empty if no consistent pattern)
        print(f"Extracted base URL: {base_url}")
        
        # At minimum, should be a string
        self.assertIsInstance(base_url, str)

    def test_real_collection_parameter_extraction(self):
        """Test parameter extraction from real collection requests."""
        parser = PostmanParser(self.real_collection)
        endpoints = parser.extract_endpoints()
        
        # Find an endpoint with parameters
        endpoint_with_params = None
        for endpoint in endpoints:
            params = endpoint.raw_definition.get("parameters", [])
            if params:
                endpoint_with_params = endpoint
                break
        
        if endpoint_with_params:
            params = endpoint_with_params.raw_definition["parameters"]
            print(f"Found endpoint with {len(params)} parameters")
            
            # Check parameter structure
            for param in params:
                self.assertIn("name", param)
                self.assertIn("in", param)
                print(f"Parameter: {param['name']} ({param['in']})")
        else:
            print("No endpoints with parameters found")

    def test_real_collection_authentication_handling(self):
        """Test that authentication headers are properly excluded."""
        parser = PostmanParser(self.real_collection)
        endpoints = parser.extract_endpoints()
        
        # Check that no auth headers are included in parameters
        for endpoint in endpoints:
            params = endpoint.raw_definition.get("parameters", [])
            header_params = [p for p in params if p["in"] == "header"]
            
            auth_headers = ["authorization", "access_token", "x-api-key", "api-key"]
            for param in header_params:
                param_name_lower = param["name"].lower()
                self.assertNotIn(param_name_lower, auth_headers,
                               f"Found auth header '{param['name']}' in parameters")

    def test_real_collection_with_swagger_parser_compatibility(self):
        """Test that PostmanParser output is compatible with existing system."""
        parser = PostmanParser(self.real_collection)
        
        # Use the same interface as SwaggerParser
        result = parser.map_to_endpoints()
        
        # Should have same structure as SwaggerParser
        self.assertIn("new_endpoints", result)
        self.assertIn("endpoints_without_their_definitions", result)
        
        endpoints = result["new_endpoints"]
        self.assertIsInstance(endpoints, list)
        
        # Check that endpoints have required attributes
        if endpoints:
            first_endpoint = endpoints[0]
            self.assertHasAttr(first_endpoint, 'method')
            self.assertHasAttr(first_endpoint, 'endpoint')
            self.assertHasAttr(first_endpoint, 'raw_definition')
            self.assertHasAttr(first_endpoint, 'scenarios')
            self.assertHasAttr(first_endpoint, 'definitions')

    def assertHasAttr(self, obj, attr):
        """Helper method to check if object has attribute."""
        self.assertTrue(hasattr(obj, attr), f"Object missing required attribute: {attr}")

    def test_real_collection_schema_inference(self):
        """Test schema inference on real request bodies."""
        parser = PostmanParser(self.real_collection)
        
        # Look for requests with bodies
        items = self.real_collection.get("item", [])
        body_found = False
        
        for item in items:
            request = item.get("request", {})
            body = request.get("body", {})
            
            if body.get("mode") == "raw" and body.get("raw"):
                body_found = True
                raw_content = body["raw"]
                
                try:
                    # Try to parse as JSON
                    json_data = json.loads(raw_content)
                    schema = parser._infer_json_schema(json_data)
                    
                    print(f"Inferred schema for request body: {schema}")
                    
                    # Should have basic schema structure
                    self.assertIn("type", schema)
                    
                    if schema["type"] == "object":
                        self.assertIn("properties", schema)
                    
                except json.JSONDecodeError:
                    # Non-JSON body, should handle gracefully
                    print(f"Non-JSON body found: {raw_content[:100]}...")
        
        if not body_found:
            print("No request bodies found in collection")

    def test_real_collection_error_handling(self):
        """Test that parser handles any problematic requests gracefully."""
        parser = PostmanParser(self.real_collection)
        
        # Should not raise exceptions during processing
        try:
            endpoints = parser.extract_endpoints()
            # Should return some endpoints or empty list, not crash
            self.assertIsInstance(endpoints, list)
            print(f"Successfully processed collection, found {len(endpoints)} endpoints")
            
        except Exception as e:
            self.fail(f"Parser should handle collection gracefully, but raised: {e}")


if __name__ == "__main__":
    unittest.main()