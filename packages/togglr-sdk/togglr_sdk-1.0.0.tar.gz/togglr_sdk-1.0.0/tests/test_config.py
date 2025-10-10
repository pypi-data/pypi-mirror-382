"""Tests for the configuration classes."""

import pytest

from togglr import ClientConfig, BackoffConfig, CacheConfig


class TestBackoffConfig:
    """Test cases for BackoffConfig class."""
    
    def test_default_values(self):
        """Test default values."""
        config = BackoffConfig()
        assert config.base_delay == 0.1
        assert config.max_delay == 2.0
        assert config.factor == 2.0
    
    def test_calculate_delay(self):
        """Test delay calculation."""
        config = BackoffConfig(base_delay=0.1, max_delay=1.0, factor=2.0)
        
        # First attempt (attempt=0) should return base_delay
        assert config.calculate_delay(0) == 0.1
        
        # Second attempt (attempt=1) should return base_delay * factor
        assert config.calculate_delay(1) == 0.2
        
        # Third attempt (attempt=2) should return base_delay * factor^2
        assert config.calculate_delay(2) == 0.4
        
        # Fourth attempt (attempt=3) should return base_delay * factor^3
        assert config.calculate_delay(3) == 0.8
        
        # Fifth attempt (attempt=4) should be capped at max_delay
        assert config.calculate_delay(4) == 1.0
        
        # Sixth attempt (attempt=5) should still be capped at max_delay
        assert config.calculate_delay(5) == 1.0


class TestCacheConfig:
    """Test cases for CacheConfig class."""
    
    def test_default_values(self):
        """Test default values."""
        config = CacheConfig()
        assert config.enabled is False
        assert config.max_size == 100
        assert config.ttl_seconds == 5.0
    
    def test_custom_values(self):
        """Test custom values."""
        config = CacheConfig(enabled=True, max_size=500, ttl_seconds=30.0)
        assert config.enabled is True
        assert config.max_size == 500
        assert config.ttl_seconds == 30.0


class TestClientConfig:
    """Test cases for ClientConfig class."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = ClientConfig.default("test-api-key")
        
        assert config.api_key == "test-api-key"
        assert config.base_url == "http://localhost:8090"
        assert config.timeout == 0.8
        assert config.retries == 2
        assert config.max_connections == 100
        assert isinstance(config.backoff, BackoffConfig)
        assert isinstance(config.cache, CacheConfig)
        assert config.logger is None
        assert config.metrics is None
    
    def test_with_base_url(self):
        """Test setting base URL."""
        config = ClientConfig.default("test-api-key").with_base_url("https://api.example.com")
        assert config.base_url == "https://api.example.com"
    
    def test_with_timeout(self):
        """Test setting timeout."""
        config = ClientConfig.default("test-api-key").with_timeout(2.0)
        assert config.timeout == 2.0
    
    def test_with_retries(self):
        """Test setting retries."""
        config = ClientConfig.default("test-api-key").with_retries(5)
        assert config.retries == 5
    
    def test_with_cache(self):
        """Test setting cache configuration."""
        config = ClientConfig.default("test-api-key").with_cache(enabled=True, max_size=1000, ttl_seconds=60)
        
        assert config.cache.enabled is True
        assert config.cache.max_size == 1000
        assert config.cache.ttl_seconds == 60
    
    def test_with_backoff(self):
        """Test setting backoff configuration."""
        config = ClientConfig.default("test-api-key").with_backoff(base_delay=0.5, max_delay=10.0, factor=1.5)
        
        assert config.backoff.base_delay == 0.5
        assert config.backoff.max_delay == 10.0
        assert config.backoff.factor == 1.5
    
    def test_with_logger(self):
        """Test setting logger."""
        def custom_logger(message: str, **kwargs):
            pass
        
        config = ClientConfig.default("test-api-key").with_logger(custom_logger)
        assert config.logger is custom_logger
    
    def test_with_metrics(self):
        """Test setting metrics."""
        class CustomMetrics:
            pass
        
        metrics = CustomMetrics()
        config = ClientConfig.default("test-api-key").with_metrics(metrics)
        assert config.metrics is metrics
    
    def test_with_insecure(self):
        """Test setting insecure mode."""
        config = ClientConfig.default("test-api-key").with_insecure()
        assert config.insecure is True
    
    def test_with_ssl_ca_cert(self):
        """Test setting SSL CA certificate file."""
        config = ClientConfig.default("test-api-key").with_ssl_ca_cert("/path/to/ca.pem")
        assert config.ssl_ca_cert == "/path/to/ca.pem"
    
    def test_with_client_cert(self):
        """Test setting client certificate files."""
        config = ClientConfig.default("test-api-key").with_client_cert("/path/to/cert.pem", "/path/to/key.pem")
        assert config.cert_file == "/path/to/cert.pem"
        assert config.key_file == "/path/to/key.pem"
    
    def test_with_client_cert_no_key(self):
        """Test setting client certificate without key file."""
        config = ClientConfig.default("test-api-key").with_client_cert("/path/to/cert.pem")
        assert config.cert_file == "/path/to/cert.pem"
        assert config.key_file is None
    
    def test_with_ca_cert_data_string(self):
        """Test setting CA certificate data as string."""
        cert_data = "-----BEGIN CERTIFICATE-----\nMII...\n-----END CERTIFICATE-----"
        config = ClientConfig.default("test-api-key").with_ca_cert_data(cert_data)
        assert config.ca_cert_data == cert_data
    
    def test_with_ca_cert_data_bytes(self):
        """Test setting CA certificate data as bytes."""
        cert_data = b"-----BEGIN CERTIFICATE-----\nMII...\n-----END CERTIFICATE-----"
        config = ClientConfig.default("test-api-key").with_ca_cert_data(cert_data)
        assert config.ca_cert_data == cert_data
    
    def test_with_ssl_hostname_verification(self):
        """Test setting SSL hostname verification."""
        config = ClientConfig.default("test-api-key").with_ssl_hostname_verification(False)
        assert config.assert_hostname is False
        
        config = ClientConfig.default("test-api-key").with_ssl_hostname_verification(True)
        assert config.assert_hostname is True
    
    def test_with_tls_server_name(self):
        """Test setting TLS server name."""
        config = ClientConfig.default("test-api-key").with_tls_server_name("api.example.com")
        assert config.tls_server_name == "api.example.com"
    
    def test_tls_default_values(self):
        """Test default TLS values."""
        config = ClientConfig.default("test-api-key")
        assert config.ssl_ca_cert is None
        assert config.cert_file is None
        assert config.key_file is None
        assert config.ca_cert_data is None
        assert config.assert_hostname is None
        assert config.tls_server_name is None
        assert config.insecure is False
    
    def test_chaining(self):
        """Test method chaining."""
        def custom_logger(message: str, **kwargs):
            pass
        
        class CustomMetrics:
            pass
        
        metrics = CustomMetrics()
        
        config = ClientConfig.default("test-api-key") \
            .with_base_url("https://api.example.com") \
            .with_timeout(3.0) \
            .with_retries(4) \
            .with_cache(enabled=True, max_size=2000, ttl_seconds=120) \
            .with_backoff(base_delay=0.2, max_delay=5.0, factor=1.8) \
            .with_logger(custom_logger) \
            .with_metrics(metrics) \
            .with_ssl_ca_cert("/path/to/ca.pem") \
            .with_client_cert("/path/to/cert.pem", "/path/to/key.pem") \
            .with_tls_server_name("api.example.com")
        
        assert config.api_key == "test-api-key"
        assert config.base_url == "https://api.example.com"
        assert config.timeout == 3.0
        assert config.retries == 4
        assert config.cache.enabled is True
        assert config.cache.max_size == 2000
        assert config.cache.ttl_seconds == 120
        assert config.backoff.base_delay == 0.2
        assert config.backoff.max_delay == 5.0
        assert config.backoff.factor == 1.8
        assert config.logger is custom_logger
        assert config.metrics is metrics
        assert config.ssl_ca_cert == "/path/to/ca.pem"
        assert config.cert_file == "/path/to/cert.pem"
        assert config.key_file == "/path/to/key.pem"
        assert config.tls_server_name == "api.example.com"
