"""Configuration classes for togglr-sdk-python."""

import time
from typing import Optional, Callable, Any, Union
from dataclasses import dataclass, field


@dataclass
class BackoffConfig:
    """Configuration for retry backoff."""
    
    base_delay: float = 0.1  # 100ms
    max_delay: float = 2.0   # 2s
    factor: float = 2.0
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for the given attempt."""
        delay = self.base_delay
        for _ in range(1, attempt):
            delay *= self.factor
            if delay > self.max_delay:
                delay = self.max_delay
                break
        return delay


@dataclass
class CacheConfig:
    """Configuration for caching."""
    
    enabled: bool = False
    max_size: int = 100
    ttl_seconds: float = 5.0


@dataclass
class ClientConfig:
    """Configuration for the Togglr client."""
    
    # Required
    api_key: str
    
    # Optional with defaults
    base_url: str = "http://localhost:8090"
    timeout: float = 0.8  # 800ms
    retries: int = 2
    backoff: BackoffConfig = field(default_factory=BackoffConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    max_connections: int = 100
    insecure: bool = False
    
    # TLS/SSL configuration
    ssl_ca_cert: Optional[str] = None  # Path to CA certificate file
    cert_file: Optional[str] = None    # Path to client certificate file
    key_file: Optional[str] = None     # Path to client private key file
    ca_cert_data: Optional[Union[str, bytes]] = None  # CA certificate data (PEM/DER)
    assert_hostname: Optional[bool] = None  # SSL hostname verification
    tls_server_name: Optional[str] = None   # TLS Server Name Indication (SNI)
    
    # Optional callbacks
    logger: Optional[Callable[[str, Any], None]] = None
    metrics: Optional[Any] = None  # Will be typed properly when metrics are implemented
    
    @classmethod
    def default(cls, api_key: str) -> "ClientConfig":
        """Create a default configuration with the provided API key."""
        return cls(api_key=api_key)
    
    def with_base_url(self, base_url: str) -> "ClientConfig":
        """Set the base URL."""
        self.base_url = base_url
        return self
    
    def with_timeout(self, timeout: float) -> "ClientConfig":
        """Set the timeout in seconds."""
        self.timeout = timeout
        return self
    
    def with_retries(self, retries: int) -> "ClientConfig":
        """Set the number of retries."""
        self.retries = retries
        return self
    
    def with_cache(self, enabled: bool = True, max_size: int = 100, ttl_seconds: float = 5.0) -> "ClientConfig":
        """Configure caching."""
        self.cache = CacheConfig(enabled=enabled, max_size=max_size, ttl_seconds=ttl_seconds)
        return self
    
    def with_backoff(self, base_delay: float = 0.1, max_delay: float = 2.0, factor: float = 2.0) -> "ClientConfig":
        """Configure retry backoff."""
        self.backoff = BackoffConfig(base_delay=base_delay, max_delay=max_delay, factor=factor)
        return self
    
    def with_logger(self, logger: Callable[[str, Any], None]) -> "ClientConfig":
        """Set a custom logger."""
        self.logger = logger
        return self
    
    def with_metrics(self, metrics: Any) -> "ClientConfig":
        """Set custom metrics."""
        self.metrics = metrics
        return self
    
    def with_insecure(self) -> "ClientConfig":
        """Enable insecure mode (skip SSL verification)."""
        self.insecure = True
        return self
    
    def with_ssl_ca_cert(self, ssl_ca_cert: str) -> "ClientConfig":
        """Set the path to CA certificate file."""
        self.ssl_ca_cert = ssl_ca_cert
        return self
    
    def with_client_cert(self, cert_file: str, key_file: Optional[str] = None) -> "ClientConfig":
        """Set client certificate and key files."""
        self.cert_file = cert_file
        if key_file is not None:
            self.key_file = key_file
        return self
    
    def with_ca_cert_data(self, ca_cert_data: Union[str, bytes]) -> "ClientConfig":
        """Set CA certificate data (PEM or DER format)."""
        self.ca_cert_data = ca_cert_data
        return self
    
    def with_ssl_hostname_verification(self, assert_hostname: bool) -> "ClientConfig":
        """Enable or disable SSL hostname verification."""
        self.assert_hostname = assert_hostname
        return self
    
    def with_tls_server_name(self, tls_server_name: str) -> "ClientConfig":
        """Set TLS Server Name Indication (SNI)."""
        self.tls_server_name = tls_server_name
        return self
