"""
Tests for ScenarioService execution history behavior.

These tests ensure that the skip_execution_history flag is properly
passed through when executing scenarios for validation generation.
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from service.ScenarioService import execute_scenario_only


class TestScenarioServiceExecutionHistory:
    """Test suite for ScenarioService execution history functionality."""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return Mock(spec=Session)
    
    @patch('service.UnifiedScenarioExecution.execute_scenario_unified')
    def test_execute_scenario_only_default_saves_history(self, mock_unified, mock_db):
        """Test that execute_scenario_only saves history by default."""
        mock_unified.return_value = {
            "success": True,
            "scenario_id": 1,
            "scenario_name": "Test Scenario",
            "status_code": 200,
            "headers": {},
            "body": {"message": "success"},
            "request_details": {}
        }
        
        result = execute_scenario_only(mock_db, 1, "user123")
        
        # Verify execute_scenario_unified was called with skip_execution_history=False (default)
        mock_unified.assert_called_once_with(mock_db, 1, "user123", False)
        assert result["success"] is True
    
    @patch('service.UnifiedScenarioExecution.execute_scenario_unified')
    def test_execute_scenario_only_skips_history_when_requested(self, mock_unified, mock_db):
        """Test that execute_scenario_only skips history when skip_execution_history=True."""
        mock_unified.return_value = {
            "success": True,
            "scenario_id": 1,
            "scenario_name": "Test Scenario",
            "status_code": 200,
            "headers": {},
            "body": {"message": "success"},
            "request_details": {}
        }
        
        result = execute_scenario_only(mock_db, 1, "user123", skip_execution_history=True)
        
        # Verify execute_scenario_unified was called with skip_execution_history=True
        mock_unified.assert_called_once_with(mock_db, 1, "user123", True)
        assert result["success"] is True
    
    @patch('service.UnifiedScenarioExecution.execute_scenario_unified')
    def test_execute_scenario_only_preserves_error_response(self, mock_unified, mock_db):
        """Test that execute_scenario_only preserves error responses when skipping history."""
        mock_unified.return_value = {
            "success": False,
            "scenario_id": 1,
            "scenario_name": "Test Scenario",
            "error": "HTTP request failed"
        }
        
        result = execute_scenario_only(mock_db, 1, "user123", skip_execution_history=True)
        
        # Verify execute_scenario_unified was called with skip_execution_history=True
        mock_unified.assert_called_once_with(mock_db, 1, "user123", True)
        assert result["success"] is False
        assert result["error"] == "HTTP request failed"


class TestValidationGenerationIntegration:
    """Integration tests to ensure validation generation doesn't save execution history."""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return Mock(spec=Session)
    
    @patch('service.UnifiedScenarioExecution.execute_scenario_unified')
    def test_validation_generation_execution_skips_history(self, mock_unified, mock_db):
        """Test that validation generation execution doesn't save to history."""
        mock_unified.return_value = {
            "success": True,
            "scenario_id": 1,
            "scenario_name": "Test Scenario",
            "status_code": 200,
            "headers": {"Content-Type": "application/json"},
            "body": {"id": 123, "name": "test"},
            "request_details": {"method": "GET", "url": "/api/test"}
        }
        
        # Simulate how the validation generation endpoint calls execute_scenario_only
        result = execute_scenario_only(mock_db, 1, "user123", skip_execution_history=True)
        
        # Verify the unified service was called with the skip flag
        mock_unified.assert_called_once_with(mock_db, 1, "user123", True)
        
        # Verify the result is properly formatted
        assert result["success"] is True
        assert result["status_code"] == 200
        assert result["body"]["id"] == 123
        assert "request_details" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])