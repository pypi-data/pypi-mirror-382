"""Error classes for togglr-sdk-python."""

from typing import Optional


class TogglrError(Exception):
    """Base exception for all Togglr SDK errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class UnauthorizedError(TogglrError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, 401)


class BadRequestError(TogglrError):
    """Raised when the request is malformed."""
    
    def __init__(self, message: str = "Bad request"):
        super().__init__(message, 400)


class NotFoundError(TogglrError):
    """Raised when a resource is not found."""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, 404)


class InternalServerError(TogglrError):
    """Raised when the server encounters an internal error."""
    
    def __init__(self, message: str = "Internal server error"):
        super().__init__(message, 500)


class TooManyRequestsError(TogglrError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Too many requests"):
        super().__init__(message, 429)


class FeatureNotFoundError(TogglrError):
    """Raised when a feature flag is not found."""
    
    def __init__(self, message: str = "Feature not found"):
        super().__init__(message, 404)
