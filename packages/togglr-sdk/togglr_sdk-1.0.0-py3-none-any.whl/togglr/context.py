"""Request context for feature evaluation."""

from typing import Any, Dict, Optional


class RequestContext:
    """Context for feature evaluation requests."""
    
    # Predefined attribute keys
    ATTR_USER_ID = "user.id"
    ATTR_USER_EMAIL = "user.email"
    ATTR_USER_ANONYMOUS = "user.anonymous"
    ATTR_COUNTRY_CODE = "country_code"
    ATTR_REGION = "region"
    ATTR_CITY = "city"
    ATTR_MANUFACTURER = "manufacturer"
    ATTR_DEVICE_TYPE = "device_type"
    ATTR_OS = "os"
    ATTR_OS_VERSION = "os_version"
    ATTR_BROWSER = "browser"
    ATTR_BROWSER_VERSION = "browser_version"
    ATTR_LANGUAGE = "language"
    ATTR_CONNECTION_TYPE = "connection_type"
    ATTR_AGE = "age"
    ATTR_GENDER = "gender"
    ATTR_IP = "ip"
    ATTR_APP_VERSION = "app_version"
    ATTR_PLATFORM = "platform"
    
    def __init__(self, data: Optional[Dict[str, Any]] = None):
        """Initialize request context with optional data."""
        self._data = data or {}
    
    @classmethod
    def new(cls) -> "RequestContext":
        """Create a new empty request context."""
        return cls()
    
    def with_user_id(self, user_id: str) -> "RequestContext":
        """Set the user ID."""
        self._data[self.ATTR_USER_ID] = user_id
        return self
    
    def with_user_email(self, email: str) -> "RequestContext":
        """Set the user email."""
        self._data[self.ATTR_USER_EMAIL] = email
        return self
    
    def with_anonymous(self, anonymous: bool) -> "RequestContext":
        """Set whether the user is anonymous."""
        self._data[self.ATTR_USER_ANONYMOUS] = anonymous
        return self
    
    def with_country(self, country: str) -> "RequestContext":
        """Set the country code."""
        self._data[self.ATTR_COUNTRY_CODE] = country
        return self
    
    def with_region(self, region: str) -> "RequestContext":
        """Set the region."""
        self._data[self.ATTR_REGION] = region
        return self
    
    def with_city(self, city: str) -> "RequestContext":
        """Set the city."""
        self._data[self.ATTR_CITY] = city
        return self
    
    def with_manufacturer(self, manufacturer: str) -> "RequestContext":
        """Set the device manufacturer."""
        self._data[self.ATTR_MANUFACTURER] = manufacturer
        return self
    
    def with_device_type(self, device_type: str) -> "RequestContext":
        """Set the device type."""
        self._data[self.ATTR_DEVICE_TYPE] = device_type
        return self
    
    def with_os(self, os: str) -> "RequestContext":
        """Set the operating system."""
        self._data[self.ATTR_OS] = os
        return self
    
    def with_os_version(self, version: str) -> "RequestContext":
        """Set the operating system version."""
        self._data[self.ATTR_OS_VERSION] = version
        return self
    
    def with_browser(self, browser: str) -> "RequestContext":
        """Set the browser."""
        self._data[self.ATTR_BROWSER] = browser
        return self
    
    def with_browser_version(self, version: str) -> "RequestContext":
        """Set the browser version."""
        self._data[self.ATTR_BROWSER_VERSION] = version
        return self
    
    def with_language(self, language: str) -> "RequestContext":
        """Set the language."""
        self._data[self.ATTR_LANGUAGE] = language
        return self
    
    def with_connection_type(self, connection_type: str) -> "RequestContext":
        """Set the connection type."""
        self._data[self.ATTR_CONNECTION_TYPE] = connection_type
        return self
    
    def with_age(self, age: int) -> "RequestContext":
        """Set the user age."""
        self._data[self.ATTR_AGE] = age
        return self
    
    def with_gender(self, gender: str) -> "RequestContext":
        """Set the user gender."""
        self._data[self.ATTR_GENDER] = gender
        return self
    
    def with_ip(self, ip: str) -> "RequestContext":
        """Set the IP address."""
        self._data[self.ATTR_IP] = ip
        return self
    
    def with_app_version(self, version: str) -> "RequestContext":
        """Set the application version."""
        self._data[self.ATTR_APP_VERSION] = version
        return self
    
    def with_platform(self, platform: str) -> "RequestContext":
        """Set the platform."""
        self._data[self.ATTR_PLATFORM] = platform
        return self
    
    def set(self, key: str, value: Any) -> "RequestContext":
        """Set an arbitrary key-value pair."""
        self._data[key] = value
        return self
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value by key."""
        return self._data.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        return self._data.copy()
    
    def __repr__(self) -> str:
        """String representation of the context."""
        return f"RequestContext({self._data})"
