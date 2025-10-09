"""Data models for SmartTest CLI."""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum

class ExecutionStatus(Enum):
    """Execution status as defined in MVP spec."""
    SUCCESS = "success"
    HTTP_ERROR = "http_error"
    NETWORK_TIMEOUT = "network_timeout"
    NETWORK_ERROR = "network_error"
    AUTH_ERROR = "auth_error"
    UNKNOWN_ERROR = "unknown_error"

@dataclass
class AuthConfigReference:
    """Auth configuration reference (no actual credentials)."""
    id: str
    type: str  # "bearer_token", "basic_auth", "oauth2"
    token_param_name: str
    token_format: str  # e.g., "Bearer {token}"
    system_id: int

    @classmethod
    def from_dict(cls, data: dict) -> 'AuthConfigReference':
        return cls(
            id=data['id'],
            type=data['type'],
            token_param_name=data['token_param_name'],
            token_format=data['token_format'],
            system_id=data['system_id']
        )

@dataclass
class HttpRequest:
    """HTTP request definition with auth placeholders."""
    method: str
    resolved_url: str
    headers: Dict[str, str] = field(default_factory=dict)
    query: Dict[str, Any] = field(default_factory=dict)
    body: Optional[Any] = None

@dataclass
class Validation:
    """Test validation definition."""
    type: str
    config: Dict[str, Any] = field(default_factory=dict)

    # Convenience properties for common validation types
    @property
    def expect_status(self) -> Optional[int]:
        if self.type == "status_code":
            return self.config.get("expect")
        return None

    @property
    def jsonpath_expression(self) -> Optional[str]:
        if self.type == "jsonpath":
            return self.config.get("path")
        return None

    @property
    def expected_value(self) -> Any:
        return self.config.get("expect")

@dataclass
class ScenarioDefinition:
    """Complete scenario definition from API."""
    scenario: Dict[str, Any]
    request: HttpRequest
    auth_configs: Dict[str, AuthConfigReference]
    validations: List[Validation]

    @classmethod
    def from_api_response(cls, data: dict) -> 'ScenarioDefinition':
        """Create ScenarioDefinition from API response."""
        request_data = data['request']
        request = HttpRequest(
            method=request_data['method'],
            resolved_url=request_data['resolved_url'],
            headers=request_data.get('headers', {}),
            query=request_data.get('query', {}),
            body=request_data.get('body')
        )

        auth_configs = {}
        for config_id, config_data in data.get('auth_configs', {}).items():
            auth_configs[config_id] = AuthConfigReference.from_dict(config_data)

        validations = []
        for validation_data in data.get('validations', []):
            validations.append(Validation(
                type=validation_data['type'],
                config=validation_data
            ))

        return cls(
            scenario=data['scenario'],
            request=request,
            auth_configs=auth_configs,
            validations=validations
        )

    @property
    def id(self) -> int:
        return self.scenario['id']

    @property
    def name(self) -> str:
        return self.scenario['name']

@dataclass
class ValidationResult:
    """Result of a single validation check."""
    validation_id: int
    name: str
    passed: bool
    details: Optional[Dict[str, Any]] = None

@dataclass
class ScenarioResult:
    """Complete result of scenario execution."""
    scenario_id: int
    scenario_name: str
    execution_status: ExecutionStatus
    http_status: Optional[int] = None
    response_time_ms: Optional[int] = None
    validation_results: List[ValidationResult] = field(default_factory=list)
    error_details: Optional[Dict[str, Any]] = None
    run_id: Optional[str] = None

    @property
    def passed(self) -> bool:
        """True if execution was successful and all validations passed."""
        return (
            self.execution_status == ExecutionStatus.SUCCESS
            and all(v.passed for v in self.validation_results)
        )

    @property
    def failed(self) -> bool:
        """True if any validation failed (but execution was successful)."""
        return (
            self.execution_status == ExecutionStatus.SUCCESS
            and any(not v.passed for v in self.validation_results)
        )

    @property
    def error(self) -> bool:
        """True if execution failed (network, auth, etc.)."""
        return self.execution_status != ExecutionStatus.SUCCESS

@dataclass
class ExecutionSummary:
    """Summary of all scenario executions."""
    total: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    execution_time_seconds: float = 0.0

    @property
    def success_rate(self) -> float:
        """Success rate as percentage."""
        if self.total == 0:
            return 0.0
        return (self.passed / self.total) * 100.0