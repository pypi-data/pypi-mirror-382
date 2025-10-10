"""Togglr Python SDK for feature flag management."""

from .client import Client, ClientConfig
from .context import RequestContext

def new_client(api_key: str, **kwargs) -> Client:
    """Create a new Togglr client with default configuration.
    
    Args:
        api_key: API key for authentication
        **kwargs: Additional configuration options
        
    Returns:
        Configured Togglr client
    """
    # Handle cache config if passed as dict
    if 'cache' in kwargs and isinstance(kwargs['cache'], dict):
        from .config import CacheConfig
        kwargs['cache'] = CacheConfig(**kwargs['cache'])
    
    config = ClientConfig(api_key=api_key, **kwargs)
    return Client(config)
from .errors import (
    TogglrError,
    UnauthorizedError,
    BadRequestError,
    NotFoundError,
    InternalServerError,
    TooManyRequestsError,
    FeatureNotFoundError,
)
from .version import __version__

# Import generated models
from togglr_client.models.feature_error_report import FeatureErrorReport
from togglr_client.models.feature_health import FeatureHealth

__all__ = [
    "Client",
    "ClientConfig", 
    "RequestContext",
    "new_client",
    "TogglrError",
    "UnauthorizedError",
    "BadRequestError",
    "NotFoundError",
    "InternalServerError",
    "TooManyRequestsError",
    "FeatureNotFoundError",
    "FeatureErrorReport",
    "FeatureHealth",
    "__version__",
]

__version__ = "1.0.0"
