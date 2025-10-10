# Togglr Python SDK

Python SDK for working with Togglr - feature flag management system.

## Installation

```bash
pip install togglr-sdk
```

## Quick Start

```python
import togglr
from togglr import RequestContext

# Create client with default configuration
client = togglr.new_client(
    api_key="your-api-key-here",
    base_url="http://localhost:8090",
    timeout=1.0,
    cache={"enabled": True, "max_size": 1000, "ttl_seconds": 10}
)

# Use context manager for proper resource cleanup
with client:
    # Create request context
    context = RequestContext.new() \
        .with_user_id("user123") \
        .with_country("US") \
        .with_device_type("mobile") \
        .with_os("iOS") \
        .with_os_version("15.0") \
        .with_browser("Safari") \
        .with_language("en-US")
    
    # Evaluate feature flag
    try:
        value, enabled, found = client.evaluate("new_ui", context)
        if found:
            print(f"Feature enabled: {enabled}, value: {value}")
        else:
            print("Feature not found")
    except togglr.TogglrError as e:
        print(f"Error evaluating feature: {e}")
    
    # Simple enabled check
    try:
        is_enabled = client.is_enabled("new_ui", context)
        print(f"Feature is enabled: {is_enabled}")
    except togglr.FeatureNotFoundError:
        print("Feature not found")
    except togglr.TogglrError as e:
        print(f"Error checking feature: {e}")
    
    # With default value
    is_enabled = client.is_enabled_or_default("new_ui", context, default=False)
    print(f"Feature enabled (with default): {is_enabled}")
```

## Configuration

### Creating a client

```python
# With default settings
client = togglr.new_client("api-key")

# With custom configuration
client = togglr.new_client(
    api_key="api-key",
    base_url="https://api.togglr.com",
    timeout=2.0,
    retries=3,
    cache={"enabled": True, "max_size": 1000, "ttl_seconds": 10},
    insecure=True  # Skip SSL verification for self-signed certificates
)
```

### TLS/SSL Configuration

The SDK supports comprehensive TLS/SSL configuration for secure connections:

```python
# Using with_ methods
config = ClientConfig.default("api-key") \
    .with_base_url("https://api.togglr.com") \
    .with_ssl_ca_cert("/path/to/ca-certificate.pem") \
    .with_client_cert("/path/to/client-cert.pem", "/path/to/client-key.pem") \
    .with_tls_server_name("api.togglr.com") \
    .with_ssl_hostname_verification(True)

client = Client(config)

# Using new_client with TLS parameters
client = togglr.new_client(
    api_key="api-key",
    base_url="https://api.togglr.com",
    ssl_ca_cert="/path/to/ca-certificate.pem",
    cert_file="/path/to/client-cert.pem",
    key_file="/path/to/client-key.pem",
    ca_cert_data="-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
    tls_server_name="api.togglr.com",
    assert_hostname=True
)

# Using CA certificate data instead of file
config = ClientConfig.default("api-key") \
    .with_ca_cert_data("-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----")

# Insecure mode (only for testing)
config = ClientConfig.default("api-key") \
    .with_insecure()  # Disables SSL certificate verification
```

#### Available TLS Options

- `ssl_ca_cert`: Path to CA certificate file
- `cert_file`: Path to client certificate file  
- `key_file`: Path to client private key file
- `ca_cert_data`: CA certificate data (PEM or DER format)
- `assert_hostname`: Enable/disable SSL hostname verification
- `tls_server_name`: TLS Server Name Indication (SNI)
- `insecure`: Skip SSL verification (for testing only)

### Advanced configuration

```python
from togglr import Client, ClientConfig, RequestContext

# Create custom configuration
config = ClientConfig.default("api-key") \
    .with_base_url("https://api.togglr.com") \
    .with_timeout(2.0) \
    .with_retries(3) \
    .with_cache(enabled=True, max_size=1000, ttl_seconds=10) \
    .with_backoff(base_delay=0.2, max_delay=5.0, factor=1.5)

client = Client(config)
```

## Usage

### Creating request context

```python
context = RequestContext.new() \
    .with_user_id("user123") \
    .with_user_email("user@example.com") \
    .with_country("US") \
    .with_device_type("mobile") \
    .with_os("iOS") \
    .with_os_version("15.0") \
    .with_browser("Safari") \
    .with_language("en-US") \
    .with_age(25) \
    .with_gender("female") \
    .set("custom_attribute", "custom_value")
```

### Evaluating feature flags

```python
# Full evaluation
value, enabled, found = client.evaluate("feature_key", context)

# Simple enabled check
is_enabled = client.is_enabled("feature_key", context)

# With default value
is_enabled = client.is_enabled_or_default("feature_key", context, default=False)
```

### Health check

```python
if client.health_check():
    print("API is healthy")
else:
    print("API is not healthy")
```

### Error Reporting and Auto-Disable

The SDK supports reporting feature execution errors for auto-disable functionality:

```python
# Report an error for a feature
client.report_error(
    feature_key="feature_key",
    error_type="timeout",
    error_message="Service did not respond in 5s",
    context={
        "service": "payment-gateway",
        "timeout_ms": 5000,
        "retry_count": 3
    }
)

print("Error reported successfully - queued for processing")
```

### Feature Health Monitoring

Check the health status of features:

```python
# Get feature health status
health = client.get_feature_health("feature_key")
print(f"Feature Health:")
print(f"  Enabled: {health.enabled}")
print(f"  Auto Disabled: {health.auto_disabled}")
if health.error_rate is not None:
    print(f"  Error Rate: {health.error_rate * 100:.2f}%")
if health.last_error_at is not None:
    print(f"  Last Error: {health.last_error_at}")

# Simple health check
is_healthy = client.is_feature_healthy("feature_key")
print(f"Feature is healthy: {is_healthy}")
```

## Caching

The SDK supports optional caching of evaluation results:

```python
client = togglr.new_client(
    api_key="api-key",
    cache={"enabled": True, "max_size": 1000, "ttl_seconds": 10}
)
```

## Retries

The SDK automatically retries requests on temporary errors:

```python
config = ClientConfig.default("api-key") \
    .with_retries(3) \
    .with_backoff(base_delay=0.1, max_delay=2.0, factor=2.0)

client = Client(config)
```

## Logging and Metrics

```python
def custom_logger(message: str, **kwargs):
    print(f"[LOG] {message} {kwargs}")

class CustomMetrics:
    def inc_evaluate_request(self):
        # Increment request counter
        pass
    
    def inc_cache_hit(self):
        # Increment cache hit counter
        pass
    
    def inc_evaluate_error(self, error_code: str):
        # Increment error counter
        pass
    
    def observe_evaluate_latency(self, latency: float):
        # Observe evaluation latency
        pass

config = ClientConfig.default("api-key") \
    .with_logger(custom_logger) \
    .with_metrics(CustomMetrics())

client = Client(config)
```

## Error Handling

```python
try:
    value, enabled, found = client.evaluate("feature_key", context)
except togglr.UnauthorizedError:
    # Authorization error
    pass
except togglr.BadRequestError:
    # Bad request
    pass
except togglr.NotFoundError:
    # Resource not found
    pass
except togglr.InternalServerError:
    # Internal server error
    pass
except togglr.TooManyRequestsError:
    # Rate limit exceeded
    pass
except togglr.FeatureNotFoundError:
    # Feature flag not found
    pass
except togglr.TogglrError as e:
    # Other errors
    print(f"Error: {e}")
```

### Error Report Types

```python
# Create different types of error reports
client.report_error(
    feature_key="feature_key",
    error_type="timeout",
    error_message="Service timeout",
    context={"service": "payment-gateway", "timeout_ms": 5000}
)

client.report_error(
    feature_key="feature_key",
    error_type="validation",
    error_message="Invalid data",
    context={"field": "email", "error_code": "INVALID_FORMAT"}
)

client.report_error(
    feature_key="feature_key",
    error_type="service_unavailable",
    error_message="Service down",
    context={"service": "database", "status_code": 503}
)
```

### Feature Health Types

```python
# FeatureHealth provides detailed health information
from togglr import FeatureHealth

# Access health properties
health = client.get_feature_health("feature_key")
print(f"Feature Key: {health.feature_key}")
print(f"Environment Key: {health.environment_key}")
print(f"Enabled: {health.enabled}")
print(f"Auto Disabled: {health.auto_disabled}")
print(f"Error Rate: {health.error_rate}")  # Optional
print(f"Threshold: {health.threshold}")    # Optional
print(f"Last Error At: {health.last_error_at}")  # Optional
```

## Client Generation

To update the generated client from OpenAPI specification:

```bash
make generate
```

## Building and Testing

```bash
# Install development dependencies
make dev-install

# Build
make build

# Testing
make test

# Linting
make lint

# Format code
make format

# Clean
make clean
```

## Examples

Complete usage examples are located in the `examples/` directory:

- `simple_example.py` - Simple usage example
- `advanced_example.py` - Advanced example with custom configuration
- `tls_example.py` - TLS/SSL configuration examples

## Requirements

- Python 3.8+
- httpx
- pydantic
- cachetools (optional)
