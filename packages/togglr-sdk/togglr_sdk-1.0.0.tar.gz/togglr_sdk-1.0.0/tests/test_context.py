"""Tests for the RequestContext class."""

import pytest

from togglr import RequestContext


class TestRequestContext:
    """Test cases for the RequestContext class."""
    
    def test_new_context(self):
        """Test creating a new context."""
        context = RequestContext.new()
        assert isinstance(context, RequestContext)
        assert context.to_dict() == {}
    
    def test_context_with_data(self):
        """Test creating context with initial data."""
        data = {"user.id": "user123", "country": "US"}
        context = RequestContext(data)
        assert context.to_dict() == data
    
    def test_with_user_id(self):
        """Test setting user ID."""
        context = RequestContext.new().with_user_id("user123")
        assert context.get("user.id") == "user123"
        assert context.get(RequestContext.ATTR_USER_ID) == "user123"
    
    def test_with_user_email(self):
        """Test setting user email."""
        context = RequestContext.new().with_user_email("user@example.com")
        assert context.get("user.email") == "user@example.com"
        assert context.get(RequestContext.ATTR_USER_EMAIL) == "user@example.com"
    
    def test_with_country(self):
        """Test setting country."""
        context = RequestContext.new().with_country("US")
        assert context.get("country_code") == "US"
        assert context.get(RequestContext.ATTR_COUNTRY_CODE) == "US"
    
    def test_with_device_type(self):
        """Test setting device type."""
        context = RequestContext.new().with_device_type("mobile")
        assert context.get("device_type") == "mobile"
        assert context.get(RequestContext.ATTR_DEVICE_TYPE) == "mobile"
    
    def test_with_os(self):
        """Test setting OS."""
        context = RequestContext.new().with_os("iOS")
        assert context.get("os") == "iOS"
        assert context.get(RequestContext.ATTR_OS) == "iOS"
    
    def test_with_os_version(self):
        """Test setting OS version."""
        context = RequestContext.new().with_os_version("15.0")
        assert context.get("os_version") == "15.0"
        assert context.get(RequestContext.ATTR_OS_VERSION) == "15.0"
    
    def test_with_browser(self):
        """Test setting browser."""
        context = RequestContext.new().with_browser("Safari")
        assert context.get("browser") == "Safari"
        assert context.get(RequestContext.ATTR_BROWSER) == "Safari"
    
    def test_with_language(self):
        """Test setting language."""
        context = RequestContext.new().with_language("en-US")
        assert context.get("language") == "en-US"
        assert context.get(RequestContext.ATTR_LANGUAGE) == "en-US"
    
    def test_with_age(self):
        """Test setting age."""
        context = RequestContext.new().with_age(25)
        assert context.get("age") == 25
        assert context.get(RequestContext.ATTR_AGE) == 25
    
    def test_with_gender(self):
        """Test setting gender."""
        context = RequestContext.new().with_gender("female")
        assert context.get("gender") == "female"
        assert context.get(RequestContext.ATTR_GENDER) == "female"
    
    def test_set_custom_attribute(self):
        """Test setting custom attributes."""
        context = RequestContext.new().set("custom_key", "custom_value")
        assert context.get("custom_key") == "custom_value"
    
    def test_chaining(self):
        """Test method chaining."""
        context = RequestContext.new() \
            .with_user_id("user123") \
            .with_country("US") \
            .with_device_type("mobile") \
            .with_os("iOS") \
            .set("custom", "value")
        
        expected = {
            "user.id": "user123",
            "country_code": "US",
            "device_type": "mobile",
            "os": "iOS",
            "custom": "value"
        }
        
        assert context.to_dict() == expected
    
    def test_get_with_default(self):
        """Test getting value with default."""
        context = RequestContext.new()
        assert context.get("nonexistent", "default") == "default"
        assert context.get("nonexistent") is None
    
    def test_repr(self):
        """Test string representation."""
        context = RequestContext.new().with_user_id("user123")
        repr_str = repr(context)
        assert "RequestContext" in repr_str
        assert "user.id" in repr_str
        assert "user123" in repr_str
