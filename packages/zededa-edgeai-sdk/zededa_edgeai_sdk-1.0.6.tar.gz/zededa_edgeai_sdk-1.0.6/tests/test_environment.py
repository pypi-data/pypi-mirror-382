"""Test cases for environment and configuration utilities."""

import os
import unittest
from unittest.mock import patch

from zededa_edgeai_sdk.config import get_service_url
from zededa_edgeai_sdk.environment import (
    APPLIED_ENVIRONMENT_KEYS,
    apply_environment,
    clear_environment,
    sanitize_credentials,
    _mask_string,
)
from zededa_edgeai_sdk.exceptions import (
    AuthenticationError,
    CatalogNotFoundError,
    MultipleCatalogsError,
    UserCancelledError,
    ZededaSDKError,
)


class TestConfig(unittest.TestCase):
    """Test configuration management."""

    def setUp(self):
        """Set up test environment."""
        self.env_backup = os.environ.copy()

    def tearDown(self):
        """Restore environment after tests."""
        os.environ.clear()
        os.environ.update(self.env_backup)

    def test_get_service_url_default(self):
        """Test getting default service URL."""
        os.environ.pop("EDGEAI_SERVICE_URL", None)
        url = get_service_url()
        self.assertEqual(url, "https://studio.edgeai.zededa.dev")

    def test_get_service_url_from_env(self):
        """Test getting service URL from environment variable."""
        os.environ["EDGEAI_SERVICE_URL"] = "https://custom.backend.com/"
        url = get_service_url()
        self.assertEqual(url, "https://custom.backend.com")  # trailing slash stripped

    def test_get_service_url_strips_trailing_slash(self):
        """Test that service URL strips trailing slash."""
        os.environ["EDGEAI_SERVICE_URL"] = "https://example.com///"
        url = get_service_url()
        self.assertEqual(url, "https://example.com")


class TestEnvironment(unittest.TestCase):
    """Test environment variable management."""

    def setUp(self):
        """Set up test environment."""
        self.env_backup = os.environ.copy()
        # Clear SDK environment variables
        for key in APPLIED_ENVIRONMENT_KEYS:
            os.environ.pop(key, None)

    def tearDown(self):
        """Restore environment after tests."""
        os.environ.clear()
        os.environ.update(self.env_backup)

    def test_applied_environment_keys_constant(self):
        """Test that APPLIED_ENVIRONMENT_KEYS contains expected keys."""
        expected_keys = [
            "EDGEAI_CURRENT_CATALOG",
            "EDGEAI_ACCESS_TOKEN",
            "MLFLOW_TRACKING_TOKEN",
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "MLFLOW_S3_ENDPOINT_URL",
            "MLFLOW_TRACKING_URI",
            "MINIO_BUCKET",
            "EDGEAI_BACKEND_URL",
        ]
        
        for key in expected_keys:
            self.assertIn(key, APPLIED_ENVIRONMENT_KEYS)

    def test_apply_environment_complete_credentials(self):
        """Test applying complete credential set to environment."""
        credentials = {
            "catalog_id": "development",
            "backend_jwt": "jwt_token_123",
            "aws_access_key_id": "access_key_123",
            "aws_secret_access_key": "secret_key_123",
            "endpoint_url": "https://minio.example.com",
            "mlflow_tracking_uri": "https://mlflow.example.com",
            "bucket": "my-bucket",
            "service_url": "https://backend.com"
        }
        
        env_vars = apply_environment(credentials, "development")
        
        # Check environment variables were set
        self.assertEqual(os.environ["EDGEAI_CURRENT_CATALOG"], "development")
        self.assertEqual(os.environ["EDGEAI_ACCESS_TOKEN"], "jwt_token_123")
        self.assertEqual(os.environ["MLFLOW_TRACKING_TOKEN"], "jwt_token_123")
        self.assertEqual(os.environ["AWS_ACCESS_KEY_ID"], "access_key_123")
        self.assertEqual(os.environ["AWS_SECRET_ACCESS_KEY"], "secret_key_123")
        self.assertEqual(os.environ["MLFLOW_S3_ENDPOINT_URL"], "https://minio.example.com")
        self.assertEqual(os.environ["MLFLOW_TRACKING_URI"], "https://mlflow.example.com")
        self.assertEqual(os.environ["MINIO_BUCKET"], "my-bucket")
        self.assertEqual(os.environ["EDGEAI_BACKEND_URL"], "https://backend.com")
        
        # Check return value matches what was set
        self.assertEqual(env_vars["EDGEAI_CURRENT_CATALOG"], "development")

    def test_apply_environment_partial_credentials(self):
        """Test applying partial credential set to environment."""
        credentials = {
            "catalog_id": "test",
            "backend_jwt": "token123",
            "service_url": "https://backend.com"
            # Missing some fields
        }
        
        env_vars = apply_environment(credentials, "test")
        
        # Check required fields were set
        self.assertEqual(os.environ["EDGEAI_CURRENT_CATALOG"], "test")
        self.assertEqual(os.environ["EDGEAI_ACCESS_TOKEN"], "token123")
        self.assertEqual(os.environ["EDGEAI_BACKEND_URL"], "https://backend.com")
        
        # Check optional fields not in environment when None
        self.assertNotIn("AWS_ACCESS_KEY_ID", os.environ)
        self.assertNotIn("MLFLOW_S3_ENDPOINT_URL", os.environ)

    def test_clear_environment(self):
        """Test clearing SDK environment variables."""
        # Set some environment variables
        os.environ["EDGEAI_CURRENT_CATALOG"] = "test"
        os.environ["MLFLOW_TRACKING_TOKEN"] = "token123"
        os.environ["AWS_ACCESS_KEY_ID"] = "access_key"
        os.environ["SOME_OTHER_VAR"] = "should_remain"
        
        clear_environment()
        
        # Check SDK variables were cleared
        self.assertNotIn("EDGEAI_CURRENT_CATALOG", os.environ)
        self.assertNotIn("MLFLOW_TRACKING_TOKEN", os.environ)
        self.assertNotIn("AWS_ACCESS_KEY_ID", os.environ)
        
        # Check non-SDK variable remained
        self.assertEqual(os.environ["SOME_OTHER_VAR"], "should_remain")

    def test_mask_string_long_value(self):
        """Test string masking with long values."""
        result = _mask_string("this_is_a_very_long_secret_token_12345")
        self.assertEqual(result, "this_i...2345")

    def test_mask_string_short_value(self):
        """Test string masking with short values."""
        result = _mask_string("short")
        self.assertEqual(result, "***")

    def test_mask_string_edge_case_length(self):
        """Test string masking with edge case length."""
        result = _mask_string("exactly10c")  # exactly 10 chars
        self.assertEqual(result, "***")
        
        result = _mask_string("exactly11ch")  # 11 chars - should show parts
        self.assertEqual(result, "exactl...11ch")

    def test_sanitize_credentials_complete(self):
        """Test credential sanitization with complete data."""
        credentials = {
            "catalog_id": "development",
            "backend_jwt": "very_long_jwt_token_12345",
            "access_token": "access_token_67890",
            "aws_access_key_id": "AKIAIOSFODNN7EXAMPLE",
            "aws_secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
            "password": "user_password_123",
            "public_field": "should_not_be_masked",
            "environment": {
                "MLFLOW_TRACKING_TOKEN": "tracking_token_12345",
                "MLFLOW_TRACKING_URI": "https://mlflow.example.com",
                "SOME_PUBLIC_VAR": "public_value"
            }
        }
        
        result = sanitize_credentials(credentials)
        
        # Check sensitive fields were masked
        self.assertEqual(result["backend_jwt"], "very_l...2345")
        self.assertEqual(result["access_token"], "access...7890")
        self.assertEqual(result["aws_access_key_id"], "AKIAIO...MPLE")
        self.assertEqual(result["aws_secret_access_key"], "wJalrX...EKEY")
        self.assertEqual(result["password"], "user_p..._123")
        
        # Check non-sensitive field not masked
        self.assertEqual(result["public_field"], "should_not_be_masked")
        self.assertEqual(result["catalog_id"], "development")
        
        # Check environment variables
        self.assertEqual(result["environment"]["MLFLOW_TRACKING_TOKEN"], "tracki...2345")
        self.assertEqual(result["environment"]["MLFLOW_TRACKING_URI"], "https://mlflow.example.com")
        self.assertEqual(result["environment"]["SOME_PUBLIC_VAR"], "public_value")

    def test_sanitize_credentials_missing_fields(self):
        """Test credential sanitization with missing fields."""
        credentials = {
            "catalog_id": "test",
            "backend_jwt": None,  # None value
            "some_field": ""  # Empty string
        }
        
        result = sanitize_credentials(credentials)
        
        # Check None values handled
        self.assertIsNone(result["backend_jwt"])
        self.assertEqual(result["some_field"], "")
        self.assertEqual(result["catalog_id"], "test")

    def test_sanitize_credentials_short_sensitive_values(self):
        """Test credential sanitization with short sensitive values."""
        credentials = {
            "token": "abc",  # Very short
            "password": "pass",  # Short
            "secret_key": "secret123456"  # Longer
        }
        
        result = sanitize_credentials(credentials)
        
        self.assertEqual(result["token"], "***")
        self.assertEqual(result["password"], "***")
        self.assertEqual(result["secret_key"], "secret...3456")


class TestExceptions(unittest.TestCase):
    """Test custom exception classes."""

    def test_zededa_sdk_error_inheritance(self):
        """Test that all custom exceptions inherit from ZededaSDKError."""
        self.assertTrue(issubclass(AuthenticationError, ZededaSDKError))
        self.assertTrue(issubclass(CatalogNotFoundError, ZededaSDKError))
        self.assertTrue(issubclass(MultipleCatalogsError, ZededaSDKError))
        self.assertTrue(issubclass(UserCancelledError, ZededaSDKError))

    def test_zededa_sdk_error_is_exception(self):
        """Test that ZededaSDKError inherits from Exception."""
        self.assertTrue(issubclass(ZededaSDKError, Exception))

    def test_exception_creation_and_messages(self):
        """Test creating exceptions with custom messages."""
        auth_error = AuthenticationError("Login failed")
        self.assertEqual(str(auth_error), "Login failed")
        
        catalog_error = CatalogNotFoundError("Catalog 'test' not found")
        self.assertEqual(str(catalog_error), "Catalog 'test' not found")
        
        multiple_error = MultipleCatalogsError("Multiple catalogs available")
        self.assertEqual(str(multiple_error), "Multiple catalogs available")
        
        cancelled_error = UserCancelledError("User cancelled operation")
        self.assertEqual(str(cancelled_error), "User cancelled operation")

    def test_exception_raising_and_catching(self):
        """Test raising and catching custom exceptions."""
        with self.assertRaises(AuthenticationError):
            raise AuthenticationError("Test error")
        
        with self.assertRaises(ZededaSDKError):
            raise AuthenticationError("Test error")  # Should be caught as base class
        
        with self.assertRaises(Exception):
            raise AuthenticationError("Test error")  # Should be caught as Exception


if __name__ == "__main__":
    unittest.main()