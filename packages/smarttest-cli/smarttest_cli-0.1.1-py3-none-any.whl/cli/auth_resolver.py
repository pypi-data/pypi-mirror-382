"""
Auth configuration resolution system with zero credential exposure.

This module implements the critical security feature of the CLI:
- Auth configs are resolved locally within the customer network
- No credentials are ever sent to or received from the SmartTest backend
- Supports multiple auth types with extensible architecture
"""

import os
import json
import re
from typing import Dict, Any, Optional
from dataclasses import dataclass

from .models import AuthConfigReference, HttpRequest

class AuthResolutionError(Exception):
    """Raised when authentication resolution fails."""
    pass

@dataclass
class ResolvedAuth:
    """Resolved authentication credentials (stays local)."""
    config_id: str
    resolved_value: str
    auth_type: str

class AuthResolver:
    """
    Resolves auth configuration references to actual credentials locally.

    This is the core security component - ensures zero credential exposure by:
    1. Receiving only auth config metadata from backend
    2. Resolving actual tokens/credentials within customer network
    3. Replacing placeholders in request templates
    4. Never exposing credentials outside the customer environment
    """

    def __init__(self):
        self._resolved_cache: Dict[str, ResolvedAuth] = {}

    def resolve_auth_configs(
        self,
        auth_configs: Dict[str, AuthConfigReference],
        request: HttpRequest
    ) -> HttpRequest:
        """
        Resolve all auth configurations and replace placeholders in the request.

        Args:
            auth_configs: Auth configuration references from API
            request: HTTP request template with ${auth_config_id} placeholders

        Returns:
            HTTP request with resolved authentication values

        Security guarantee: All credential resolution happens locally
        """
        resolved_auths = {}

        # Resolve each auth configuration
        for config_id, config_ref in auth_configs.items():
            try:
                resolved_auth = self._resolve_single_auth_config(config_ref)
                resolved_auths[config_id] = resolved_auth

                # Cache for potential reuse within same execution
                self._resolved_cache[config_id] = resolved_auth

            except Exception as e:
                raise AuthResolutionError(
                    f"Failed to resolve auth config '{config_id}': {e}"
                )

        # Replace placeholders in the request
        resolved_request = self._replace_auth_placeholders(request, resolved_auths)

        return resolved_request

    def _resolve_single_auth_config(self, config: AuthConfigReference) -> ResolvedAuth:
        """
        Resolve a single auth configuration to actual credentials.

        Supports multiple auth types as per MVP specification.
        All resolution happens within customer network using local environment.
        """

        if config.type == "bearer_token":
            return self._resolve_bearer_token(config)
        elif config.type == "basic_auth":
            return self._resolve_basic_auth(config)
        elif config.type == "api_key":
            return self._resolve_api_key(config)
        else:
            raise AuthResolutionError(
                f"Unsupported auth type: {config.type}. "
                f"Supported types: bearer_token, basic_auth, api_key"
            )

    def _resolve_bearer_token(self, config: AuthConfigReference) -> ResolvedAuth:
        """Resolve bearer token authentication."""

        # Look for token in environment variables (most common pattern)
        # Try multiple common naming patterns
        potential_env_names = [
            f"{config.id.upper()}_TOKEN",
            f"{config.id.upper()}",
            f"SYSTEM_{config.system_id}_TOKEN",
            f"SYSTEM_{config.system_id}_BEARER_TOKEN",
        ]

        token = None
        for env_name in potential_env_names:
            token = os.getenv(env_name)
            if token:
                break

        if not token:
            raise AuthResolutionError(
                f"Bearer token not found for '{config.id}'. "
                f"Set one of: {', '.join(potential_env_names)}"
            )

        # Format according to configuration
        formatted_value = config.token_format.format(token=token)

        return ResolvedAuth(
            config_id=config.id,
            resolved_value=formatted_value,
            auth_type=config.type
        )

    def _resolve_basic_auth(self, config: AuthConfigReference) -> ResolvedAuth:
        """Resolve basic authentication (username:password)."""

        # Look for username and password in environment
        username_env = f"{config.id.upper()}_USERNAME"
        password_env = f"{config.id.upper()}_PASSWORD"

        username = os.getenv(username_env)
        password = os.getenv(password_env)

        if not username or not password:
            raise AuthResolutionError(
                f"Basic auth credentials not found for '{config.id}'. "
                f"Set both {username_env} and {password_env}"
            )

        # Create basic auth value
        import base64
        credentials = f"{username}:{password}"
        encoded = base64.b64encode(credentials.encode()).decode('ascii')
        formatted_value = config.token_format.format(token=f"Basic {encoded}")

        return ResolvedAuth(
            config_id=config.id,
            resolved_value=formatted_value,
            auth_type=config.type
        )

    def _resolve_api_key(self, config: AuthConfigReference) -> ResolvedAuth:
        """Resolve API key authentication."""

        # Look for API key in environment
        potential_env_names = [
            f"{config.id.upper()}_API_KEY",
            f"{config.id.upper()}_KEY",
            f"{config.id.upper()}",
        ]

        api_key = None
        for env_name in potential_env_names:
            api_key = os.getenv(env_name)
            if api_key:
                break

        if not api_key:
            raise AuthResolutionError(
                f"API key not found for '{config.id}'. "
                f"Set one of: {', '.join(potential_env_names)}"
            )

        formatted_value = config.token_format.format(token=api_key)

        return ResolvedAuth(
            config_id=config.id,
            resolved_value=formatted_value,
            auth_type=config.type
        )

    def _replace_auth_placeholders(
        self,
        request: HttpRequest,
        resolved_auths: Dict[str, ResolvedAuth]
    ) -> HttpRequest:
        """
        Replace ${auth_config_id} placeholders with resolved auth values.

        Handles placeholders in headers, query parameters, and request body.
        """

        # Create new request object (don't modify original)
        resolved_request = HttpRequest(
            method=request.method,
            resolved_url=request.resolved_url,
            headers=request.headers.copy(),
            query=request.query.copy(),
            body=request.body
        )

        # Replace placeholders in headers
        for header_name, header_value in resolved_request.headers.items():
            resolved_request.headers[header_name] = self._replace_placeholders_in_string(
                header_value, resolved_auths
            )

        # Replace placeholders in query parameters
        for query_name, query_value in resolved_request.query.items():
            if isinstance(query_value, str):
                resolved_request.query[query_name] = self._replace_placeholders_in_string(
                    query_value, resolved_auths
                )

        # Replace placeholders in request body (if string or dict)
        if isinstance(resolved_request.body, str):
            resolved_request.body = self._replace_placeholders_in_string(
                resolved_request.body, resolved_auths
            )
        elif isinstance(resolved_request.body, dict):
            resolved_request.body = self._replace_placeholders_in_dict(
                resolved_request.body, resolved_auths
            )

        return resolved_request

    def _replace_placeholders_in_string(
        self,
        text: str,
        resolved_auths: Dict[str, ResolvedAuth]
    ) -> str:
        """Replace ${auth_config_id} placeholders in a string."""

        def replacer(match):
            config_id = match.group(1)
            if config_id in resolved_auths:
                return resolved_auths[config_id].resolved_value
            else:
                # Leave unresolved placeholders as-is (might not be auth-related)
                return match.group(0)

        # Pattern matches ${config_id}
        return re.sub(r'\$\{([^}]+)\}', replacer, text)

    def _replace_placeholders_in_dict(
        self,
        data: Dict[str, Any],
        resolved_auths: Dict[str, ResolvedAuth]
    ) -> Dict[str, Any]:
        """Recursively replace placeholders in dictionary values."""

        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = self._replace_placeholders_in_string(value, resolved_auths)
            elif isinstance(value, dict):
                result[key] = self._replace_placeholders_in_dict(value, resolved_auths)
            elif isinstance(value, list):
                result[key] = self._replace_placeholders_in_list(value, resolved_auths)
            else:
                result[key] = value
        return result

    def _replace_placeholders_in_list(
        self,
        data: list,
        resolved_auths: Dict[str, ResolvedAuth]
    ) -> list:
        """Recursively replace placeholders in list items."""

        result = []
        for item in data:
            if isinstance(item, str):
                result.append(self._replace_placeholders_in_string(item, resolved_auths))
            elif isinstance(item, dict):
                result.append(self._replace_placeholders_in_dict(item, resolved_auths))
            elif isinstance(item, list):
                result.append(self._replace_placeholders_in_list(item, resolved_auths))
            else:
                result.append(item)
        return result

    def clear_cache(self):
        """Clear the resolved auth cache (for security)."""
        self._resolved_cache.clear()