import unittest
import json
from postmanParser import PostmanParser


class TestPostmanParser(unittest.TestCase):
    """Test suite for PostmanParser class following TDD approach."""

    def setUp(self):
        """Set up test fixtures with various Postman collection examples."""
        # Basic collection structure
        self.basic_collection = {
            "info": {
                "name": "Test API",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": [
                {
                    "name": "Get Users",
                    "request": {
                        "method": "GET",
                        "url": "https://api.test.com/users"
                    }
                }
            ]
        }

        # Collection with variables
        self.collection_with_variables = {
            "info": {
                "name": "API with Variables",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "variable": [
                {"key": "baseUrl", "value": "https://api.example.com"},
                {"key": "apiVersion", "value": "v1"}
            ],
            "item": [
                {
                    "name": "Get Users",
                    "request": {
                        "method": "GET", 
                        "url": "{{baseUrl}}/{{apiVersion}}/users"
                    }
                }
            ]
        }

        # Collection with environment
        self.test_environment = {
            "name": "Test Environment",
            "values": [
                {"key": "baseUrl", "value": "https://test-api.example.com"},
                {"key": "apiKey", "value": "test-key-123"}
            ]
        }

        # Collection with structured URL
        self.collection_with_structured_url = {
            "info": {
                "name": "Structured URL Test",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": [
                {
                    "name": "Get Product",
                    "request": {
                        "method": "GET",
                        "url": {
                            "raw": "https://api.shop.com/products/123?category=electronics",
                            "protocol": "https",
                            "host": ["api", "shop", "com"],
                            "path": ["products", "123"],
                            "query": [
                                {"key": "category", "value": "electronics"},
                                {"key": "debug", "value": "true", "disabled": True}
                            ]
                        }
                    }
                }
            ]
        }

        # Collection with body and headers
        self.collection_with_body = {
            "info": {
                "name": "API with Body",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": [
                {
                    "name": "Create User",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"},
                            {"key": "X-API-Key", "value": "secret-key", "disabled": True},
                            {"key": "User-Agent", "value": "PostmanRuntime/7.28.0"}
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": '{"name": "John Doe", "email": "john@example.com", "age": 30}',
                            "options": {"raw": {"language": "json"}}
                        },
                        "url": "https://api.test.com/users"
                    }
                }
            ]
        }

        # Collection with folders
        self.collection_with_folders = {
            "info": {
                "name": "API with Folders",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": [
                {
                    "name": "Users",
                    "item": [
                        {
                            "name": "Get All Users",
                            "request": {
                                "method": "GET",
                                "url": "https://api.test.com/users"
                            }
                        },
                        {
                            "name": "Create User",
                            "request": {
                                "method": "POST",
                                "url": "https://api.test.com/users"
                            }
                        }
                    ]
                }
            ]
        }

        # Invalid collection
        self.invalid_collection = {
            "info": {
                "name": "Invalid Collection"
                # Missing schema
            },
            "item": []
        }

    def test_basic_collection_parsing(self):
        """Test parsing a basic Postman collection."""
        parser = PostmanParser(self.basic_collection)
        
        # Test validation
        self.assertTrue(parser.validate_collection_format())
        
        # Test collection info extraction
        info = parser.extract_collection_info()
        self.assertEqual(info["name"], "Test API")
        
        # Test endpoint extraction
        endpoints = parser.extract_endpoints()
        self.assertEqual(len(endpoints), 1)
        
        endpoint = endpoints[0]
        self.assertEqual(endpoint.method, "GET")
        self.assertEqual(endpoint.endpoint, "/users")

    def test_variable_resolution(self):
        """Test variable resolution with collection variables."""
        parser = PostmanParser(self.collection_with_variables)
        
        # Test variable extraction
        self.assertEqual(parser.variables["baseUrl"], "https://api.example.com")
        self.assertEqual(parser.variables["apiVersion"], "v1")
        
        # Test variable resolution
        resolved = parser.resolve_variables("{{baseUrl}}/{{apiVersion}}/test")
        self.assertEqual(resolved, "https://api.example.com/v1/test")
        
        # Test endpoint extraction with variables
        endpoints = parser.extract_endpoints()
        self.assertEqual(len(endpoints), 1)
        self.assertEqual(endpoints[0].endpoint, "/v1/users")

    def test_environment_selection(self):
        """Test environment variable resolution."""
        parser = PostmanParser(self.collection_with_variables, self.test_environment)
        
        # Environment should override collection variables
        endpoints = parser.extract_endpoints(self.test_environment)
        
        # Check that base URL was extracted from environment
        base_url = parser.extract_base_url()
        self.assertEqual(base_url, "https://test-api.example.com")

    def test_structured_url_processing(self):
        """Test processing of structured URL objects."""
        parser = PostmanParser(self.collection_with_structured_url)
        endpoints = parser.extract_endpoints()
        
        self.assertEqual(len(endpoints), 1)
        endpoint = endpoints[0]
        self.assertEqual(endpoint.method, "GET")
        self.assertEqual(endpoint.endpoint, "/products/123")
        
        # Check query parameters were extracted
        params = endpoint.raw_definition.get("parameters", [])
        query_params = [p for p in params if p["in"] == "query"]
        self.assertEqual(len(query_params), 1)  # Only enabled query param
        self.assertEqual(query_params[0]["name"], "category")

    def test_body_and_headers_processing(self):
        """Test processing of request bodies and headers."""
        parser = PostmanParser(self.collection_with_body)
        endpoints = parser.extract_endpoints()
        
        self.assertEqual(len(endpoints), 1)
        endpoint = endpoints[0]
        self.assertEqual(endpoint.method, "POST")
        
        params = endpoint.raw_definition.get("parameters", [])
        
        # Check headers (excluding disabled ones and auth headers)
        header_params = [p for p in params if p["in"] == "header"]
        self.assertEqual(len(header_params), 2)  # Content-Type and User-Agent
        
        # Check body parameter
        body_params = [p for p in params if p["in"] == "body"]
        self.assertEqual(len(body_params), 1)
        
        body_param = body_params[0]
        self.assertIn("schema", body_param)
        self.assertEqual(body_param["schema"]["type"], "object")

    def test_folder_processing(self):
        """Test processing of nested folders."""
        parser = PostmanParser(self.collection_with_folders)
        endpoints = parser.extract_endpoints()
        
        self.assertEqual(len(endpoints), 2)  # Both requests in folder
        methods = [ep.method for ep in endpoints]
        self.assertIn("GET", methods)
        self.assertIn("POST", methods)

    def test_invalid_collection_handling(self):
        """Test handling of invalid collection format."""
        parser = PostmanParser(self.invalid_collection)
        self.assertFalse(parser.validate_collection_format())

    def test_schema_inference(self):
        """Test JSON schema inference from request bodies."""
        parser = PostmanParser(self.collection_with_body)
        
        # Test schema inference directly
        test_data = {"name": "John", "age": 30, "active": True}
        schema = parser._infer_json_schema(test_data)
        
        self.assertEqual(schema["type"], "object")
        self.assertIn("properties", schema)
        self.assertEqual(schema["properties"]["name"]["type"], "string")
        self.assertEqual(schema["properties"]["age"]["type"], "integer")
        self.assertEqual(schema["properties"]["active"]["type"], "boolean")

    def test_type_inference(self):
        """Test parameter type inference."""
        parser = PostmanParser(self.basic_collection)
        
        # Test different types
        self.assertEqual(parser._infer_type("123"), "integer")
        self.assertEqual(parser._infer_type("12.34"), "number")
        self.assertEqual(parser._infer_type("hello"), "string")
        self.assertEqual(parser._infer_type(True), "boolean")
        self.assertEqual(parser._infer_type([1, 2, 3]), "array")
        self.assertEqual(parser._infer_type({"key": "value"}), "object")

    def test_base_url_extraction(self):
        """Test base URL extraction from requests."""
        parser = PostmanParser(self.basic_collection)
        base_url = parser.extract_base_url()
        self.assertEqual(base_url, "https://api.test.com")

    def test_map_to_endpoints_interface(self):
        """Test compatibility with SwaggerParser interface."""
        parser = PostmanParser(self.basic_collection)
        result = parser.map_to_endpoints()
        
        # Should have same structure as SwaggerParser
        self.assertIn("new_endpoints", result)
        self.assertIn("endpoints_without_their_definitions", result)
        
        endpoints = result["new_endpoints"]
        self.assertEqual(len(endpoints), 1)
        self.assertIsInstance(endpoints[0], object)  # EndpointBase object

    def test_get_host_interface(self):
        """Test compatibility with SwaggerParser get_host method."""
        parser = PostmanParser(self.basic_collection)
        host = parser.get_host()
        self.assertEqual(host, "https://api.test.com")

    def test_unsupported_request_skipping(self):
        """Test graceful handling of unsupported request types."""
        collection_with_errors = {
            "info": {
                "name": "Collection with Errors",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": [
                {
                    "name": "Valid Request",
                    "request": {
                        "method": "GET",
                        "url": "https://api.test.com/valid"
                    }
                },
                {
                    "name": "Invalid Request",
                    # Missing request object
                },
                {
                    "name": "Another Valid Request", 
                    "request": {
                        "method": "POST",
                        "url": "https://api.test.com/another"
                    }
                }
            ]
        }
        
        parser = PostmanParser(collection_with_errors)
        endpoints = parser.extract_endpoints()
        
        # Should process only valid requests
        self.assertEqual(len(endpoints), 2)
        methods = [ep.method for ep in endpoints]
        self.assertIn("GET", methods)
        self.assertIn("POST", methods)

    def test_authentication_header_exclusion(self):
        """Test that authentication headers are excluded from parameters."""
        collection_with_auth = {
            "info": {
                "name": "API with Auth",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": [
                {
                    "name": "Authenticated Request",
                    "request": {
                        "method": "GET",
                        "header": [
                            {"key": "Authorization", "value": "Bearer token123"},
                            {"key": "access_token", "value": "secret123"},
                            {"key": "Content-Type", "value": "application/json"},
                            {"key": "X-Custom-Header", "value": "custom-value"}
                        ],
                        "url": "https://api.test.com/data"
                    }
                }
            ]
        }
        
        parser = PostmanParser(collection_with_auth)
        endpoints = parser.extract_endpoints()
        
        self.assertEqual(len(endpoints), 1)
        params = endpoints[0].raw_definition.get("parameters", [])
        header_params = [p for p in params if p["in"] == "header"]
        
        # Should only include non-auth headers
        header_names = [p["name"] for p in header_params]
        self.assertIn("Content-Type", header_names)
        self.assertIn("X-Custom-Header", header_names)
        self.assertNotIn("Authorization", header_names)
        self.assertNotIn("access_token", header_names)


if __name__ == "__main__":
    unittest.main()