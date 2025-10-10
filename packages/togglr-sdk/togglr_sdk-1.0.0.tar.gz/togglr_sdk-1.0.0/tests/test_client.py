"""Tests for the main client functionality."""

import pytest
from unittest.mock import Mock, patch

from togglr import Client, ClientConfig, RequestContext
from togglr.errors import TogglrError, FeatureNotFoundError


class TestClient:
    """Test cases for the Client class."""
    
    def test_client_initialization(self):
        """Test client initialization."""
        config = ClientConfig.default("test-api-key")
        client = Client(config)
        
        assert client.config.api_key == "test-api-key"
        assert client.config.base_url == "http://localhost:8090"
        assert client.config.timeout == 0.8
        assert client.config.retries == 2
    
    def test_client_context_manager(self):
        """Test client as context manager."""
        config = ClientConfig.default("test-api-key")
        
        with Client(config) as client:
            assert isinstance(client, Client)
    
    @patch('togglr.client.DefaultApi')
    def test_health_check_success(self, mock_api_class):
        """Test successful health check."""
        mock_api = Mock()
        mock_api_class.return_value = mock_api
        mock_response = Mock()
        mock_response.status = "ok"
        mock_api.sdk_v1_health_get.return_value = mock_response
        
        config = ClientConfig.default("test-api-key")
        client = Client(config)
        
        assert client.health_check() is True
    
    @patch('togglr.client.DefaultApi')
    def test_health_check_failure(self, mock_api_class):
        """Test failed health check."""
        mock_api = Mock()
        mock_api_class.return_value = mock_api
        mock_api.sdk_v1_health_get.side_effect = Exception("API Error")
        
        config = ClientConfig.default("test-api-key")
        client = Client(config)
        
        assert client.health_check() is False
    
    @patch('togglr.client.DefaultApi')
    def test_evaluate_success(self, mock_api_class):
        """Test successful feature evaluation."""
        mock_api = Mock()
        mock_api_class.return_value = mock_api
        
        # Mock the evaluate response
        mock_response = Mock()
        mock_response.value = "test_value"
        mock_response.enabled = True
        mock_response.found = True
        
        # Mock the API call
        mock_api.sdk_v1_features_feature_key_evaluate_post.return_value = mock_response
        
        config = ClientConfig.default("test-api-key")
        client = Client(config)
        
        context = RequestContext.new().with_user_id("user123")
        value, enabled, found = client.evaluate("test_feature", context)
        
        assert value == "test_value"
        assert enabled is True
        assert found is True
    
    @patch('togglr.client.DefaultApi')
    def test_evaluate_not_found(self, mock_api_class):
        """Test feature not found."""
        mock_api = Mock()
        mock_api_class.return_value = mock_api
        
        # Mock the evaluate response for not found
        mock_response = Mock()
        mock_response.value = ""
        mock_response.enabled = False
        mock_response.found = False
        
        mock_api.sdk_v1_features_feature_key_evaluate_post.return_value = mock_response
        
        config = ClientConfig.default("test-api-key")
        client = Client(config)
        
        context = RequestContext.new().with_user_id("user123")
        value, enabled, found = client.evaluate("test_feature", context)
        
        assert value == ""
        assert enabled is False
        assert found is False
    
    @patch('togglr.client.DefaultApi')
    def test_is_enabled_success(self, mock_api_class):
        """Test successful is_enabled check."""
        mock_api = Mock()
        mock_api_class.return_value = mock_api
        
        mock_response = Mock()
        mock_response.value = "test_value"
        mock_response.enabled = True
        mock_response.found = True
        
        mock_api.sdk_v1_features_feature_key_evaluate_post.return_value = mock_response
        
        config = ClientConfig.default("test-api-key")
        client = Client(config)
        
        context = RequestContext.new().with_user_id("user123")
        is_enabled = client.is_enabled("test_feature", context)
        
        assert is_enabled is True
    
    @patch('togglr.client.DefaultApi')
    def test_is_enabled_not_found(self, mock_api_class):
        """Test is_enabled with feature not found."""
        mock_api = Mock()
        mock_api_class.return_value = mock_api
        
        mock_response = Mock()
        mock_response.value = ""
        mock_response.enabled = False
        mock_response.found = False
        
        mock_api.sdk_v1_features_feature_key_evaluate_post.return_value = mock_response
        
        config = ClientConfig.default("test-api-key")
        client = Client(config)
        
        context = RequestContext.new().with_user_id("user123")
        
        with pytest.raises(FeatureNotFoundError):
            client.is_enabled("test_feature", context)
    
    @patch('togglr.client.DefaultApi')
    def test_is_enabled_or_default_success(self, mock_api_class):
        """Test is_enabled_or_default with success."""
        mock_api = Mock()
        mock_api_class.return_value = mock_api
        
        mock_response = Mock()
        mock_response.value = "test_value"
        mock_response.enabled = True
        mock_response.found = True
        
        mock_api.sdk_v1_features_feature_key_evaluate_post.return_value = mock_response
        
        config = ClientConfig.default("test-api-key")
        client = Client(config)
        
        context = RequestContext.new().with_user_id("user123")
        is_enabled = client.is_enabled_or_default("test_feature", context, default=False)
        
        assert is_enabled is True
    
    @patch('togglr.client.DefaultApi')
    def test_is_enabled_or_default_error(self, mock_api_class):
        """Test is_enabled_or_default with error."""
        mock_api = Mock()
        mock_api_class.return_value = mock_api
        
        mock_api.sdk_v1_features_feature_key_evaluate_post.side_effect = Exception("API Error")
        
        config = ClientConfig.default("test-api-key")
        client = Client(config)
        
        context = RequestContext.new().with_user_id("user123")
        is_enabled = client.is_enabled_or_default("test_feature", context, default=False)
        
        assert is_enabled is False
    
    @patch('togglr.client.Configuration')
    @patch('togglr.client.ApiClient')
    @patch('togglr.client.DefaultApi')
    def test_client_with_tls_config(self, mock_api_class, mock_api_client_class, mock_config_class):
        """Test client initialization with TLS configuration."""
        mock_config = Mock()
        mock_config_class.return_value = mock_config
        mock_api_client = Mock()
        mock_api_client_class.return_value = mock_api_client
        mock_api_class.return_value = Mock()
        
        config = ClientConfig.default("test-api-key") \
            .with_ssl_ca_cert("/path/to/ca.pem") \
            .with_client_cert("/path/to/cert.pem", "/path/to/key.pem") \
            .with_ca_cert_data("-----BEGIN CERTIFICATE-----\nMII...\n-----END CERTIFICATE-----") \
            .with_ssl_hostname_verification(False) \
            .with_tls_server_name("api.example.com")
        
        client = Client(config)
        
        # Verify Configuration was called with correct parameters
        mock_config_class.assert_called_once_with(
            host="http://localhost:8090",
            api_key={"ApiKeyAuth": "test-api-key"}
        )
        
        # Verify TLS settings were applied
        assert mock_config.verify_ssl is True  # insecure=False by default
        assert mock_config.ssl_ca_cert == "/path/to/ca.pem"
        assert mock_config.cert_file == "/path/to/cert.pem"
        assert mock_config.key_file == "/path/to/key.pem"
        assert mock_config.ca_cert_data == "-----BEGIN CERTIFICATE-----\nMII...\n-----END CERTIFICATE-----"
        assert mock_config.assert_hostname is False
        assert mock_config.tls_server_name == "api.example.com"
    
    @patch('togglr.client.Configuration')
    @patch('togglr.client.ApiClient')
    @patch('togglr.client.DefaultApi')
    def test_client_with_insecure_mode(self, mock_api_class, mock_api_client_class, mock_config_class):
        """Test client initialization with insecure mode."""
        mock_config = Mock()
        mock_config_class.return_value = mock_config
        mock_api_client = Mock()
        mock_api_client_class.return_value = mock_api_client
        mock_api_class.return_value = Mock()
        
        config = ClientConfig.default("test-api-key").with_insecure()
        client = Client(config)
        
        # Verify insecure mode was applied
        assert mock_config.verify_ssl is False
    
    @patch('togglr.client.Configuration')
    @patch('togglr.client.ApiClient')
    @patch('togglr.client.DefaultApi')
    def test_new_client_with_tls_kwargs(self, mock_api_class, mock_api_client_class, mock_config_class):
        """Test new_client function with TLS keyword arguments."""
        mock_config = Mock()
        mock_config_class.return_value = mock_config
        mock_api_client = Mock()
        mock_api_client_class.return_value = mock_api_client
        mock_api_class.return_value = Mock()
        
        from togglr.client import new_client
        
        client = new_client(
            "test-api-key",
            ssl_ca_cert="/path/to/ca.pem",
            cert_file="/path/to/cert.pem",
            key_file="/path/to/key.pem",
            ca_cert_data="-----BEGIN CERTIFICATE-----\nMII...\n-----END CERTIFICATE-----",
            assert_hostname=False,
            tls_server_name="api.example.com"
        )
        
        # Verify TLS settings were applied
        assert mock_config.ssl_ca_cert == "/path/to/ca.pem"
        assert mock_config.cert_file == "/path/to/cert.pem"
        assert mock_config.key_file == "/path/to/key.pem"
        assert mock_config.ca_cert_data == "-----BEGIN CERTIFICATE-----\nMII...\n-----END CERTIFICATE-----"
        assert mock_config.assert_hostname is False
        assert mock_config.tls_server_name == "api.example.com"