"""Main client implementation for togglr-sdk-python."""

import hashlib
import json
import time
from typing import Any, Dict, Optional, Tuple, Union

from togglr_client import ApiClient, Configuration
from togglr_client.api.default_api import DefaultApi
from togglr_client.models.evaluate_response import EvaluateResponse
from togglr_client.models.feature_error_report import FeatureErrorReport
from togglr_client.models.feature_health import FeatureHealth
from togglr_client.exceptions import ApiException

from .cache import LRUCache
from .config import ClientConfig, CacheConfig
from .context import RequestContext
from .errors import (
    TogglrError,
    UnauthorizedError,
    BadRequestError,
    NotFoundError,
    InternalServerError,
    TooManyRequestsError,
    FeatureNotFoundError,
)


class Client:
    """Togglr SDK client for feature flag evaluation."""
    
    def __init__(self, config: ClientConfig):
        """Initialize the client with configuration.
        
        Args:
            config: Client configuration
        """
        self.config = config
        
        # Create API client
        api_config = Configuration(
            host=config.base_url,
            api_key={"ApiKeyAuth": config.api_key},
        )
        api_config.verify_ssl = not config.insecure
        
        # Configure TLS/SSL settings
        if config.ssl_ca_cert:
            api_config.ssl_ca_cert = config.ssl_ca_cert
        if config.cert_file:
            api_config.cert_file = config.cert_file
        if config.key_file:
            api_config.key_file = config.key_file
        if config.ca_cert_data:
            api_config.ca_cert_data = config.ca_cert_data
        if config.assert_hostname is not None:
            api_config.assert_hostname = config.assert_hostname
        if config.tls_server_name:
            api_config.tls_server_name = config.tls_server_name
        
        api_client = ApiClient(api_config)
        self._api_client = DefaultApi(api_client)
        
        # Initialize cache if enabled
        self._cache: Optional[LRUCache] = None
        if config.cache.enabled:
            self._cache = LRUCache(config.cache.max_size, config.cache.ttl_seconds)
    
    def close(self) -> None:
        """Close the client and clean up resources."""
        if self._cache:
            self._cache.clear()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def health_check(self) -> bool:
        """Perform a health check on the API.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            response = self._api_client.sdk_v1_health_get()
            return response.status == "ok"
        except Exception:
            return False
    
    def evaluate(
        self, 
        feature_key: str, 
        context: RequestContext
    ) -> Tuple[str, bool, bool]:
        """Evaluate a feature flag.
        
        Args:
            feature_key: The feature key to evaluate
            context: Request context
            
        Returns:
            Tuple of (value, enabled, found)
            
        Raises:
            TogglrError: If evaluation fails
        """
        return self._evaluate_with_retries(feature_key, context)
    
    def is_enabled(self, feature_key: str, context: RequestContext) -> bool:
        """Check if a feature is enabled.
        
        Args:
            feature_key: The feature key to check
            context: Request context
            
        Returns:
            True if enabled, False otherwise
            
        Raises:
            TogglrError: If evaluation fails
            FeatureNotFoundError: If feature is not found
        """
        value, enabled, found = self.evaluate(feature_key, context)
        if not found:
            raise FeatureNotFoundError(f"Feature '{feature_key}' not found")
        return enabled
    
    def is_enabled_or_default(
        self, 
        feature_key: str, 
        context: RequestContext, 
        default: bool = False
    ) -> bool:
        """Check if a feature is enabled, returning default on error.
        
        Args:
            feature_key: The feature key to check
            context: Request context
            default: Default value to return on error
            
        Returns:
            True if enabled, default value on error
        """
        try:
            return self.is_enabled(feature_key, context)
        except Exception as e:
            if self.config.logger:
                self.config.logger(f"Evaluation failed, using default: {e}")
            return default
    
    def report_error(
        self, 
        feature_key: str, 
        error_type: str, 
        error_message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Report a feature execution error for auto-disable functionality.
        
        Args:
            feature_key: The feature key to report error for
            error_type: Type of error (e.g., 'timeout', 'validation', 'service_unavailable')
            error_message: Human-readable error message
            context: Optional context data for the error
            
        Raises:
            TogglrError: If error reporting fails
        """
        self._report_error_with_retries(feature_key, error_type, error_message, context)
    
    def get_feature_health(self, feature_key: str) -> FeatureHealth:
        """Get the health status of a feature.
        
        Args:
            feature_key: The feature key to get health for
            
        Returns:
            FeatureHealth object with health information
            
        Raises:
            TogglrError: If health retrieval fails
        """
        return self._get_feature_health_with_retries(feature_key)
    
    def is_feature_healthy(self, feature_key: str) -> bool:
        """Check if a feature is healthy (enabled and not auto-disabled).
        
        Args:
            feature_key: The feature key to check
            
        Returns:
            True if feature is healthy, False otherwise
            
        Raises:
            TogglrError: If health check fails
        """
        health = self.get_feature_health(feature_key)
        return health.enabled and not health.auto_disabled
    
    def _evaluate_with_retries(
        self, 
        feature_key: str, 
        context: RequestContext
    ) -> Tuple[str, bool, bool]:
        """Evaluate feature with retry logic."""
        # Check cache first
        if self._cache:
            cache_key = self._get_cache_key(feature_key, context)
            entry, hit = self._cache.get(cache_key)
            if hit:
                return entry.value, entry.enabled, entry.found
        
        last_error = None
        
        for attempt in range(self.config.retries + 1):
            if attempt > 0:
                # Calculate backoff delay
                delay = self.config.backoff.calculate_delay(attempt)
                time.sleep(delay)
            
            try:
                value, enabled, found = self._evaluate_single(feature_key, context)
                
                # Cache result if successful
                if self._cache:
                    cache_key = self._get_cache_key(feature_key, context)
                    self._cache.set(cache_key, value, enabled, found)
                
                return value, enabled, found
                
            except Exception as e:
                last_error = e
                if not self._should_retry(e):
                    break
        
        # Convert API exceptions to our error types
        if isinstance(last_error, ApiException):
            raise self._convert_api_exception(last_error)
        
        raise TogglrError(f"Evaluation failed: {last_error}")
    
    def _evaluate_single(
        self, 
        feature_key: str, 
        context: RequestContext
    ) -> Tuple[str, bool, bool]:
        """Perform a single evaluation request."""
        try:
            response = self._api_client.sdk_v1_features_feature_key_evaluate_post(
                feature_key=feature_key,
                request_body=context.to_dict()
            )
            
            if isinstance(response, EvaluateResponse):
                return response.value, response.enabled, True
            else:
                # Handle error responses
                return "", False, False
                
        except ApiException as e:
            if e.status == 404:
                return "", False, False  # Feature not found, not an error
            raise e
    
    def _get_cache_key(self, feature_key: str, context: RequestContext) -> str:
        """Generate cache key for feature and context."""
        context_str = json.dumps(context.to_dict(), sort_keys=True)
        context_hash = hashlib.md5(context_str.encode()).hexdigest()
        return f"{feature_key}:{context_hash}"
    
    def _should_retry(self, error: Exception) -> bool:
        """Determine if an error should trigger a retry."""
        if isinstance(error, ApiException):
            # Don't retry on client errors (4xx)
            if 400 <= error.status < 500:
                return False
            # Retry on server errors (5xx)
            return error.status >= 500
        
        # Retry on network errors
        return True
    
    def _convert_api_exception(self, exc: ApiException) -> TogglrError:
        """Convert API exception to our error type."""
        if exc.status == 401:
            return UnauthorizedError("Authentication required")
        elif exc.status == 400:
            return BadRequestError("Bad request")
        elif exc.status == 404:
            return NotFoundError("Resource not found")
        elif exc.status == 429:
            return TooManyRequestsError("Too many requests")
        elif exc.status >= 500:
            return InternalServerError("Internal server error")
        else:
            return TogglrError(f"API error: {exc.status}")
    
    def _report_error_with_retries(
        self, 
        feature_key: str, 
        error_type: str, 
        error_message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Report error with retry logic."""
        last_error = None
        
        for attempt in range(self.config.retries + 1):
            if attempt > 0:
                # Calculate backoff delay
                delay = self.config.backoff.calculate_delay(attempt)
                time.sleep(delay)
            
            try:
                self._report_error_single(feature_key, error_type, error_message, context)
                return  # Success, exit retry loop
                
            except Exception as e:
                last_error = e
                if not self._should_retry(e):
                    break
        
        # Convert API exceptions to our error types
        if isinstance(last_error, ApiException):
            raise self._convert_api_exception(last_error)
        
        raise TogglrError(f"Error reporting failed: {last_error}")
    
    def _report_error_single(
        self, 
        feature_key: str, 
        error_type: str, 
        error_message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Perform a single error report request."""
        try:
            # Create error report
            error_report = FeatureErrorReport(
                error_type=error_type,
                error_message=error_message,
                context=context
            )
            
            # Make API call
            response = self._api_client.report_feature_error(
                feature_key=feature_key,
                feature_error_report=error_report
            )
            
            # 202 response means success - error queued for processing
            # No need to return anything, just success
            return
                
        except ApiException as e:
            if e.status == 404:
                raise NotFoundError("Feature not found")
            raise e
    
    def _get_feature_health_with_retries(self, feature_key: str) -> FeatureHealth:
        """Get feature health with retry logic."""
        last_error = None
        
        for attempt in range(self.config.retries + 1):
            if attempt > 0:
                # Calculate backoff delay
                delay = self.config.backoff.calculate_delay(attempt)
                time.sleep(delay)
            
            try:
                return self._get_feature_health_single(feature_key)
                
            except Exception as e:
                last_error = e
                if not self._should_retry(e):
                    break
        
        # Convert API exceptions to our error types
        if isinstance(last_error, ApiException):
            raise self._convert_api_exception(last_error)
        
        raise TogglrError(f"Health retrieval failed: {last_error}")
    
    def _get_feature_health_single(self, feature_key: str) -> FeatureHealth:
        """Perform a single health check request."""
        try:
            response = self._api_client.get_feature_health(feature_key=feature_key)
            
            if isinstance(response, FeatureHealth):
                return response
            else:
                # Handle error responses
                raise TogglrError(f"Unexpected response type: {type(response)}")
                
        except ApiException as e:
            if e.status == 404:
                raise NotFoundError("Feature not found")
            raise e


def new_client(api_key: str, **kwargs) -> Client:
    """Create a new client with the given API key and options.
    
    Args:
        api_key: API key for authentication
        **kwargs: Additional configuration options
        
    Returns:
        Configured client instance
    """
    config = ClientConfig.default(api_key)
    
    # Apply keyword arguments
    if "base_url" in kwargs:
        config.base_url = kwargs["base_url"]
    if "timeout" in kwargs:
        config.timeout = kwargs["timeout"]
    if "retries" in kwargs:
        config.retries = kwargs["retries"]
    if "cache" in kwargs:
        cache_config = kwargs["cache"]
        if isinstance(cache_config, dict):
            config.cache = CacheConfig(**cache_config)
        else:
            config.cache = cache_config
    if "insecure" in kwargs:
        config.insecure = kwargs["insecure"]
    
    # Apply TLS/SSL arguments
    if "ssl_ca_cert" in kwargs:
        config.ssl_ca_cert = kwargs["ssl_ca_cert"]
    if "cert_file" in kwargs:
        config.cert_file = kwargs["cert_file"]
    if "key_file" in kwargs:
        config.key_file = kwargs["key_file"]
    if "ca_cert_data" in kwargs:
        config.ca_cert_data = kwargs["ca_cert_data"]
    if "assert_hostname" in kwargs:
        config.assert_hostname = kwargs["assert_hostname"]
    if "tls_server_name" in kwargs:
        config.tls_server_name = kwargs["tls_server_name"]
    
    return Client(config)
