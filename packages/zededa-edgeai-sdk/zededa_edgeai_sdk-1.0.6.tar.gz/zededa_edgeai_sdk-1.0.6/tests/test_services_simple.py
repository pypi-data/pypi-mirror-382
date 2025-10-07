"""Test cases for the service layer components."""

import unittest
from unittest.mock import Mock

from zededa_edgeai_sdk.services.auth import AuthService
from zededa_edgeai_sdk.services.catalogs import CatalogService
from zededa_edgeai_sdk.services.http import HTTPService
from zededa_edgeai_sdk.services.storage import StorageService


class TestHTTPService(unittest.TestCase):
    """Test HTTP service functionality."""

    def setUp(self):
        """Set up HTTP service for testing."""
        self.http_service = HTTPService(debug=False)

    def test_init(self):
        """Test HTTPService initialization."""
        service = HTTPService(debug=True)
        self.assertTrue(service.debug)
        
        service = HTTPService(debug=False)
        self.assertFalse(service.debug)

    def test_mask_sensitive_value_with_sensitive_key(self):
        """Test masking of sensitive values."""
        result = self.http_service._mask_sensitive_value("token", "secret123456789")
        self.assertEqual(result, "secr...6789")

    def test_mask_sensitive_value_with_non_sensitive_key(self):
        """Test that non-sensitive keys are not masked."""
        result = self.http_service._mask_sensitive_value("username", "john_doe")
        self.assertEqual(result, "john_doe")

    def test_mask_sensitive_value_with_none(self):
        """Test masking with None value."""
        result = self.http_service._mask_sensitive_value("token", None)
        self.assertIsNone(result)

    def test_mask_sensitive_value_with_short_sensitive_value(self):
        """Test masking of short sensitive values."""
        result = self.http_service._mask_sensitive_value("password", "abc")
        self.assertEqual(result, "***")


class TestAuthService(unittest.TestCase):
    """Test authentication service functionality."""

    def setUp(self):
        """Set up AuthService for testing."""
        self.auth_service = AuthService("https://example.com", "https://ui.example.com", debug=False)

    def test_init(self):
        """Test AuthService initialization."""
        self.assertEqual(self.auth_service.backend_url, "https://example.com")
        # AuthService has these basic attributes
        self.assertTrue(hasattr(self.auth_service, 'backend_url'))
        self.assertTrue(hasattr(self.auth_service, 'debug'))

    def test_find_available_port_success(self):
        """Test finding available port."""
        # This is a simple test that the function exists and returns something
        port = self.auth_service._find_available_port()
        self.assertIsInstance(port, int)
        self.assertGreater(port, 0)

    def test_render_error_message_fallback(self):
        """Test error message rendering fallback."""
        result = self.auth_service._render_error_message({})
        expected = "Authentication failed. Please check your credentials and try again."
        self.assertEqual(result, expected)

    def test_render_error_message_with_error_param(self):
        """Test error message rendering with error parameter."""
        params = {"error": ["invalid_request"]}
        result = self.auth_service._render_error_message(params)
        # The actual implementation returns the error param directly for unrecognized errors
        self.assertEqual(result, "invalid_request")


class TestCatalogService(unittest.TestCase):
    """Test catalog service functionality."""

    def setUp(self):
        """Set up CatalogService for testing."""
        mock_http = Mock()
        self.catalog_service = CatalogService("https://example.com", mock_http)

    def test_init(self):
        """Test CatalogService initialization."""
        self.assertEqual(self.catalog_service.backend_url, "https://example.com")
        self.assertIsNotNone(self.catalog_service.http)


class TestStorageService(unittest.TestCase):
    """Test storage service functionality."""

    def setUp(self):
        """Set up StorageService for testing."""
        mock_http = Mock()
        self.storage_service = StorageService("https://example.com", mock_http)

    def test_init(self):
        """Test StorageService initialization."""
        self.assertEqual(self.storage_service.backend_url, "https://example.com")
        self.assertIsNotNone(self.storage_service.http)


if __name__ == "__main__":
    unittest.main()