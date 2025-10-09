"""Configuration management for SmartTest CLI."""

import os
import yaml
from typing import Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ProxyConfig:
    """Proxy configuration settings."""
    http_proxy: Optional[str] = None
    https_proxy: Optional[str] = None
    no_proxy: Optional[str] = None

@dataclass
class TLSConfig:
    """TLS configuration settings."""
    ca_bundle_path: Optional[str] = None
    verify_ssl: bool = True

@dataclass
class OutputConfig:
    """Output configuration settings."""
    format: str = "text"  # text, json
    show_progress: bool = True
    show_request_details: bool = False

@dataclass
class Config:
    """SmartTest CLI configuration."""
    # Required settings
    token: str

    # API settings
    api_url: str = "https://api.smarttest.com"

    # Execution settings
    concurrency: int = 5
    timeout: int = 30

    # Optional configurations
    proxy: Optional[ProxyConfig] = None
    tls: Optional[TLSConfig] = None
    output: Optional[OutputConfig] = None

    @classmethod
    def load(cls, config_file: Optional[str] = None) -> 'Config':
        """Load configuration from environment variables and optional config file."""

        # Start with required environment variables
        token = os.getenv('SMARTTEST_TOKEN')
        if not token:
            raise ValueError("SMARTTEST_TOKEN environment variable is required")

        # Default configuration
        config_data = {
            'token': token,
            'api_url': os.getenv('SMARTTEST_API_URL', 'https://api.smarttest.com'),
            'concurrency': int(os.getenv('SMARTTEST_CONCURRENCY', '5')),
            'timeout': int(os.getenv('SMARTTEST_TIMEOUT', '30')),
        }

        # Load config file if it exists
        if config_file and Path(config_file).exists():
            try:
                with open(config_file, 'r') as f:
                    file_config = yaml.safe_load(f) or {}

                # Merge file config with environment config (env takes precedence)
                config_data.update(file_config)

            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML in config file {config_file}: {e}")
            except Exception as e:
                raise ValueError(f"Could not read config file {config_file}: {e}")

        # Build nested configuration objects
        proxy_config = None
        if 'proxy' in config_data:
            proxy_config = ProxyConfig(**config_data.pop('proxy'))

        tls_config = None
        if 'tls' in config_data:
            tls_config = TLSConfig(**config_data.pop('tls'))
        else:
            tls_config = TLSConfig()  # Use defaults

        output_config = None
        if 'output' in config_data:
            output_config = OutputConfig(**config_data.pop('output'))
        else:
            output_config = OutputConfig()  # Use defaults

        return cls(
            proxy=proxy_config,
            tls=tls_config,
            output=output_config,
            **config_data
        )

    def get_request_kwargs(self) -> Dict[str, Any]:
        """Get kwargs for requests/httpx based on configuration."""
        kwargs = {
            'timeout': self.timeout,
            'verify': self.tls.verify_ssl if self.tls else True,
        }

        if self.tls and self.tls.ca_bundle_path:
            kwargs['verify'] = self.tls.ca_bundle_path

        if self.proxy:
            proxies = {}
            if self.proxy.http_proxy:
                proxies['http'] = self.proxy.http_proxy
            if self.proxy.https_proxy:
                proxies['https'] = self.proxy.https_proxy
            if proxies:
                kwargs['proxies'] = proxies

        return kwargs