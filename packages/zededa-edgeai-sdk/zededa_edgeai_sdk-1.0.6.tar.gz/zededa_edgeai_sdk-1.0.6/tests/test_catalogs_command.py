"""Test cases for the catalogs command functionality."""

import argparse
import os
import unittest
from unittest.mock import MagicMock, patch

from zededa_edgeai_sdk.commands.catalogs import (
    execute_catalog_switch,
    execute_catalog_list,
    handle_cli,
    _handle_list_command,
    _mask_value,
    CATALOGS_COMMAND,
)
from zededa_edgeai_sdk.exceptions import AuthenticationError


class TestCatalogsCommand(unittest.TestCase):
    """Test the catalogs command functionality."""

    def setUp(self):
        """Set up test environment."""
        self.env_backup = os.environ.copy()
        # Clear SDK environment variables
        for key in [
            "EDGEAI_CURRENT_CATALOG",
            "EDGEAI_ACCESS_TOKEN",
            "MLFLOW_TRACKING_TOKEN",
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "MLFLOW_S3_ENDPOINT_URL",
            "MLFLOW_TRACKING_URI",
            "MINIO_BUCKET",
            "EDGEAI_BACKEND_URL",
        ]:
            os.environ.pop(key, None)

    def tearDown(self):
        """Restore environment after tests."""
        os.environ.clear()
        os.environ.update(self.env_backup)

    def test_mask_value_with_long_string(self):
        """Test value masking with long strings."""
        result = _mask_value("very_long_secret_token_12345")
        self.assertEqual(result, "very_l...2345")

    def test_mask_value_with_short_string(self):
        """Test value masking with short strings."""
        result = _mask_value("short")
        self.assertEqual(result, "***")

    def test_mask_value_with_empty_string(self):
        """Test value masking with empty string."""
        result = _mask_value("")
        self.assertEqual(result, "***")

    def test_execute_catalog_switch_missing_catalog_id(self):
        """Test execute_catalog_switch with missing catalog ID."""
        with self.assertRaises(ValueError) as context:
            execute_catalog_switch("")
        
        self.assertIn("Catalog ID is required", str(context.exception))

        with self.assertRaises(ValueError) as context:
            execute_catalog_switch("   ")
        
        self.assertIn("Catalog ID is required", str(context.exception))

    def test_execute_catalog_switch_not_logged_in(self):
        """Test execute_catalog_switch when user is not logged in."""
        # Ensure no token in environment
        os.environ.pop("EDGEAI_ACCESS_TOKEN", None)
        
        with self.assertRaises(AuthenticationError) as context:
            execute_catalog_switch("dev")
        
        self.assertIn("Not logged in", str(context.exception))

    @patch("zededa_edgeai_sdk.commands.catalogs.ZededaEdgeAISDK")
    @patch("zededa_edgeai_sdk.commands.catalogs.apply_environment")
    @patch("zededa_edgeai_sdk.commands.catalogs.sanitize_credentials")
    def test_execute_catalog_switch_success(self, mock_sanitize, mock_apply_env, mock_sdk_class):
        """Test successful catalog switching."""
        # Set up environment with existing token
        os.environ["EDGEAI_ACCESS_TOKEN"] = "existing_token"
        
        # Mock SDK instance and methods
        mock_sdk = MagicMock()
        mock_sdk_class.return_value = mock_sdk
        mock_sdk.edgeai_backend_url = "https://test.com"
        
        # Mock catalog scoped token response
        mock_sdk._get_catalog_scoped_token.return_value = {
            "access_token": "new_scoped_token",
            "catalog_id": "dev",
            "user_permissions": ["read", "write"],
            "token_type": "bearer",
            "expires_in": 3600
        }
        
        # Mock MinIO credentials response
        mock_sdk._get_minio_credentials.return_value = {
            "aws_access_key_id": "test_access_key",
            "aws_secret_access_key": "test_secret_key",
            "endpoint_url": "https://minio.test.com",
            "bucket": "test-bucket",
            "mlflow_tracking_uri": "https://mlflow.test.com"
        }
        
        # Mock environment application
        mock_apply_env.return_value = {
            "EDGEAI_CURRENT_CATALOG": "dev",
            "AWS_ACCESS_KEY_ID": "test_access_key"
        }
        
        # Mock credential sanitization
        mock_sanitize.return_value = {
            "catalog_id": "dev",
            "aws_access_key_id": "test_a***",
            "environment": {"EDGEAI_CURRENT_CATALOG": "dev"}
        }
        
        # Execute catalog switch
        result = execute_catalog_switch("dev", service_url="https://test.com")
        
        # Verify mocks were called correctly
        mock_sdk._get_catalog_scoped_token.assert_called_once_with("existing_token", "dev")
        mock_sdk._get_minio_credentials.assert_called_once_with("new_scoped_token", "dev")
        mock_apply_env.assert_called_once()
        mock_sanitize.assert_called_once()
        
        # Verify result
        self.assertEqual(result["catalog_id"], "dev")

    def test_execute_catalog_list_not_logged_in(self):
        """Test execute_catalog_list when user is not logged in."""
        # Ensure no token in environment
        os.environ.pop("EDGEAI_ACCESS_TOKEN", None)
        
        with self.assertRaises(AuthenticationError) as context:
            execute_catalog_list()
        
        self.assertIn("Not logged in", str(context.exception))

    @patch("zededa_edgeai_sdk.commands.catalogs.ZededaEdgeAISDK")
    def test_execute_catalog_list_success(self, mock_sdk_class):
        """Test successful catalog listing."""
        # Set up environment with existing token
        os.environ["EDGEAI_ACCESS_TOKEN"] = "existing_token"
        os.environ["ZEDEDA_CURRENT_CATALOG"] = "development"
        
        # Mock SDK instance
        mock_sdk = MagicMock()
        mock_sdk_class.return_value = mock_sdk
        mock_sdk.edgeai_backend_url = "https://test.com"
        
        # Mock user info response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "user_id": "alice",
            "email": "alice@company.com",
            "name": "Alice Johnson",
            "organization_role": "superadmin",
            "all_catalogs": ["development", "production", "staging"]
        }
        mock_sdk._send_request.return_value = mock_response
        
        # Execute catalog list
        result = execute_catalog_list(service_url="https://test.com")
        
        # Verify result
        self.assertEqual(result["available_catalogs"], ["development", "production", "staging"])
        self.assertEqual(result["current_catalog"], "development")
        self.assertEqual(result["total_count"], 3)
        self.assertEqual(result["user_info"]["email"], "alice@company.com")

    @patch('zededa_edgeai_sdk.commands.catalogs._handle_list_command')
    def test_handle_cli_with_list(self, mock_handle_list):
        """Test CLI handler with --list option."""
        args = argparse.Namespace(
            service_url="https://test.com",
            debug=True,
            list=True
        )
        
        handle_cli(args)
        mock_handle_list.assert_called_once_with("https://test.com", True)

    @patch('zededa_edgeai_sdk.commands.catalogs._handle_list_command')
    def test_handle_cli_missing_params(self, mock_handle_list):
        """Test CLI handler without --list parameter."""
        args = argparse.Namespace(
            service_url=None,
            debug=False,
            list=False
        )
        
        with patch('builtins.print') as mock_print:
            with self.assertRaises(SystemExit) as cm:
                handle_cli(args)
            
            self.assertEqual(cm.exception.code, 1)
            mock_print.assert_called_with("Error: --list parameter is required")
            mock_handle_list.assert_not_called()

    def test_catalogs_command_spec(self):
        """Test that the catalogs command is properly defined."""
        self.assertEqual(CATALOGS_COMMAND.name, "catalog")
        self.assertEqual(CATALOGS_COMMAND.help, "List available catalogs")
        self.assertIsNotNone(CATALOGS_COMMAND.register)

    def test_register_creates_parser_with_options(self):
        """Test that the register function creates parser with correct options."""
        import argparse
        
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()
        
        # Register the catalog command
        CATALOGS_COMMAND.register(subparsers)
        
        # Test with --list
        args = parser.parse_args(["catalog", "--list"])
        self.assertTrue(args.list)
        
        # Test with options
        args = parser.parse_args([
            "catalog",
            "--list",
            "--service-url", "https://test.com",
            "--debug"
        ])
        self.assertTrue(args.list)
        self.assertEqual(args.service_url, "https://test.com")
        self.assertTrue(args.debug)


if __name__ == "__main__":
    unittest.main()

import argparse
import os
import unittest
from unittest.mock import MagicMock, patch

from zededa_edgeai_sdk.commands.catalogs import (
    execute_catalog_switch,
    execute_catalog_list,
    handle_cli,
    _handle_list_command,
    _mask_value,
    CATALOGS_COMMAND,
)
from zededa_edgeai_sdk.exceptions import AuthenticationError


class TestCatalogsCommand(unittest.TestCase):
    """Test the catalogs command functionality."""

    def setUp(self):
        """Set up test environment."""
        self.env_backup = os.environ.copy()
        # Clear SDK environment variables
        for key in [
            "EDGEAI_CURRENT_CATALOG",
            "EDGEAI_ACCESS_TOKEN",
            "MLFLOW_TRACKING_TOKEN",
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "MLFLOW_S3_ENDPOINT_URL",
            "MLFLOW_TRACKING_URI",
            "MINIO_BUCKET",
            "EDGEAI_BACKEND_URL",
        ]:
            os.environ.pop(key, None)

    def tearDown(self):
        """Restore environment after tests."""
        os.environ.clear()
        os.environ.update(self.env_backup)

    def test_mask_value_with_long_string(self):
        """Test value masking with long strings."""
        result = _mask_value("very_long_secret_token_12345")
        self.assertEqual(result, "very_l...2345")

    def test_mask_value_with_short_string(self):
        """Test value masking with short strings."""
        result = _mask_value("short")
        self.assertEqual(result, "***")

    def test_mask_value_with_empty_string(self):
        """Test value masking with empty string."""
        result = _mask_value("")
        self.assertEqual(result, "***")

    def test_execute_catalog_switch_missing_catalog_id(self):
        """Test execute_catalog_switch with missing catalog ID."""
        with self.assertRaises(ValueError) as context:
            execute_catalog_switch("")
        
        self.assertIn("Catalog ID is required", str(context.exception))

        with self.assertRaises(ValueError) as context:
            execute_catalog_switch("   ")
        
        self.assertIn("Catalog ID is required", str(context.exception))

    def test_execute_catalog_switch_not_logged_in(self):
        """Test execute_catalog_switch when user is not logged in."""
        # Ensure no token in environment
        os.environ.pop("EDGEAI_ACCESS_TOKEN", None)
        
        with self.assertRaises(AuthenticationError) as context:
            execute_catalog_switch("dev")
        
        self.assertIn("Not logged in", str(context.exception))

    @patch("zededa_edgeai_sdk.commands.catalogs.ZededaEdgeAISDK")
    @patch("zededa_edgeai_sdk.commands.catalogs.apply_environment")
    @patch("zededa_edgeai_sdk.commands.catalogs.sanitize_credentials")
    def test_execute_catalog_switch_success(self, mock_sanitize, mock_apply_env, mock_sdk_class):
        """Test successful catalog switching."""
        # Set up environment with existing token
        os.environ["EDGEAI_ACCESS_TOKEN"] = "existing_token"
        
        # Mock SDK instance and methods
        mock_sdk = MagicMock()
        mock_sdk_class.return_value = mock_sdk
        mock_sdk.edgeai_backend_url = "https://test.com"
        
        # Mock catalog scoped token response
        mock_sdk._get_catalog_scoped_token.return_value = {
            "access_token": "new_scoped_token",
            "catalog_id": "dev",
            "user_permissions": ["read", "write"],
            "token_type": "bearer",
            "expires_in": 3600
        }
        
        # Mock MinIO credentials response
        mock_sdk._get_minio_credentials.return_value = {
            "aws_access_key_id": "test_key",
            "aws_secret_access_key": "test_secret",
            "endpoint_url": "https://minio.test.com",
            "bucket": "test-bucket"
        }
        
        # Mock environment application
        mock_apply_env.return_value = {
            "EDGEAI_CURRENT_CATALOG": "dev",
            "MLFLOW_TRACKING_TOKEN": "new_scoped_token"
        }
        
        # Mock credential sanitization
        mock_sanitize.return_value = {
            "catalog_id": "dev",
            "permissions": ["read", "write"],
            "environment": {"EDGEAI_CURRENT_CATALOG": "dev"}
        }
        
        # Execute catalog switch
        result = execute_catalog_switch("dev", service_url="https://test.com")
        
        # Verify calls
        mock_sdk._get_catalog_scoped_token.assert_called_once_with("existing_token", "dev")
        mock_sdk._get_minio_credentials.assert_called_once_with("new_scoped_token", "dev")
        mock_apply_env.assert_called_once()
        mock_sanitize.assert_called_once()
        
        # Verify result
        self.assertEqual(result["catalog_id"], "dev")

    @patch("zededa_edgeai_sdk.commands.catalogs.ZededaEdgeAISDK")
    def test_execute_catalog_switch_catalog_token_failure(self, mock_sdk_class):
        """Test catalog switching when catalog scoped token fails."""
        # Set up environment with existing token
        os.environ["EDGEAI_ACCESS_TOKEN"] = "existing_token"
        
        # Mock SDK instance
        mock_sdk = MagicMock()
        mock_sdk_class.return_value = mock_sdk
        mock_sdk.edgeai_backend_url = "https://test.com"
        
        # Mock failed catalog scoped token response
        mock_sdk._get_catalog_scoped_token.return_value = None
        
        with self.assertRaises(AuthenticationError) as context:
            execute_catalog_switch("invalid_catalog")
        
        self.assertIn("Failed to switch to catalog", str(context.exception))

    @patch("zededa_edgeai_sdk.commands.catalogs.ZededaEdgeAISDK")
    def test_execute_catalog_switch_minio_credentials_failure(self, mock_sdk_class):
        """Test catalog switching when MinIO credentials fail."""
        # Set up environment with existing token
        os.environ["EDGEAI_ACCESS_TOKEN"] = "existing_token"
        
        # Mock SDK instance
        mock_sdk = MagicMock()
        mock_sdk_class.return_value = mock_sdk
        mock_sdk.edgeai_backend_url = "https://test.com"
        
        # Mock successful catalog scoped token but failed MinIO credentials
        mock_sdk._get_catalog_scoped_token.return_value = {
            "access_token": "new_scoped_token",
            "catalog_id": "dev",
            "user_permissions": ["read", "write"]
        }
        mock_sdk._get_minio_credentials.return_value = None
        
        with self.assertRaises(AuthenticationError) as context:
            execute_catalog_switch("dev")
        
        self.assertIn("Failed to retrieve storage credentials", str(context.exception))

    @patch("zededa_edgeai_sdk.commands.catalogs.ZededaEdgeAISDK")
    def test_execute_catalog_switch_missing_access_token(self, mock_sdk_class):
        """Test catalog switching when scoped token response is missing access_token."""
        # Set up environment with existing token
        os.environ["EDGEAI_ACCESS_TOKEN"] = "existing_token"
        
        # Mock SDK instance
        mock_sdk = MagicMock()
        mock_sdk_class.return_value = mock_sdk
        mock_sdk.edgeai_backend_url = "https://test.com"
        
        # Mock malformed catalog scoped token response
        mock_sdk._get_catalog_scoped_token.return_value = {
            "catalog_id": "dev",
            "user_permissions": ["read", "write"]
            # Missing access_token
        }
        
        with self.assertRaises(AuthenticationError) as context:
            execute_catalog_switch("dev")
        
        self.assertIn("unable to acquire catalog-scoped token", str(context.exception))

    def test_handle_cli_missing_parameters(self):
        """Test CLI handler when --list parameter is missing."""
        args = argparse.Namespace(
            list=False,
            service_url=None,
            debug=False
        )
        
        with patch('builtins.print') as mock_print:
            with self.assertRaises(SystemExit) as context:
                handle_cli(args)
            
            self.assertEqual(context.exception.code, 1)
            # Check that both error messages are printed
            mock_print.assert_any_call("Error: --list parameter is required")
            mock_print.assert_any_call("Use 'zededa-edgeai set-catalog-context <catalog>' to switch catalogs")

    def test_register_command_basic(self):
        """Test command registration creates parser correctly."""
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()
        
        # Register the command
        CATALOGS_COMMAND.register(subparsers)
        
        # Verify the command was registered
        self.assertIn("catalog", subparsers._name_parser_map)

    def test_register_command(self):
        """Test command registration creates proper parser."""
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()
        
        # Register the command
        CATALOGS_COMMAND.register(subparsers)
        
        # Verify the command was registered
        self.assertIn("catalog", subparsers._name_parser_map)
        
        # Test parsing valid arguments
        catalog_parser = subparsers._name_parser_map["catalog"]
        
        # Test with --list
        args = catalog_parser.parse_args(["--list"])
        self.assertTrue(args.list)
        self.assertIsNone(args.service_url)
        self.assertFalse(args.debug)
        
        # Test with all options
        args = catalog_parser.parse_args([
            "--list",
            "--service-url", "https://custom.backend.com",
            "--debug"
        ])
        self.assertTrue(args.list)
        self.assertEqual(args.service_url, "https://custom.backend.com")
        self.assertTrue(args.debug)

    def test_command_spec_attributes(self):
        """Test that the command spec has correct attributes."""
        self.assertEqual(CATALOGS_COMMAND.name, "catalog")
        self.assertEqual(CATALOGS_COMMAND.help, "List available catalogs")
        self.assertIsNotNone(CATALOGS_COMMAND.register)

    # Tests for catalog listing functionality
    def test_execute_catalog_list_not_logged_in(self):
        """Test execute_catalog_list when user is not logged in."""
        # Ensure no token in environment
        os.environ.pop("EDGEAI_ACCESS_TOKEN", None)
        
        with self.assertRaises(AuthenticationError) as context:
            execute_catalog_list()
        
        self.assertIn("Not logged in", str(context.exception))

    @patch("zededa_edgeai_sdk.commands.catalogs.ZededaEdgeAISDK")
    def test_execute_catalog_list_success(self, mock_sdk_class):
        """Test successful catalog listing."""
        # Set up environment with existing token
        os.environ["EDGEAI_ACCESS_TOKEN"] = "existing_token"
        os.environ["EDGEAI_CURRENT_CATALOG"] = "development"
        
        # Mock SDK instance
        mock_sdk = MagicMock()
        mock_sdk_class.return_value = mock_sdk
        mock_sdk.edgeai_backend_url = "https://test.com"
        
        # Mock user info response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "user_id": "alice",
            "email": "alice@company.com",
            "name": "Alice Johnson",
            "organization_role": "superadmin",
            "all_catalogs": ["development", "production", "staging"]
        }
        mock_sdk._send_request.return_value = mock_response
        
        # Execute catalog list
        result = execute_catalog_list(service_url="https://test.com")
        
        # Verify result
        self.assertEqual(result["available_catalogs"], ["development", "production", "staging"])
        self.assertEqual(result["current_catalog"], "development")
        self.assertEqual(result["total_count"], 3)
        self.assertEqual(result["user_info"]["email"], "alice@company.com")
        
        # Verify API call
        mock_sdk._send_request.assert_called_once_with(
            "GET",
            "https://test.com/api/v1/user-info",
            headers={"Authorization": "Bearer existing_token"}
        )

    @patch("zededa_edgeai_sdk.commands.catalogs.ZededaEdgeAISDK")
    def test_execute_catalog_list_api_failure(self, mock_sdk_class):
        """Test catalog listing when API call fails."""
        # Set up environment with existing token
        os.environ["EDGEAI_ACCESS_TOKEN"] = "existing_token"
        
        # Mock SDK instance
        mock_sdk = MagicMock()
        mock_sdk_class.return_value = mock_sdk
        
        # Mock failed API response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_sdk._send_request.return_value = mock_response
        
        with self.assertRaises(AuthenticationError) as context:
            execute_catalog_list()
        
        self.assertIn("Failed to fetch catalog list", str(context.exception))

    @patch("zededa_edgeai_sdk.commands.catalogs.execute_catalog_list")
    def test_handle_list_command_success(self, mock_execute):
        """Test CLI handler for catalog list."""
        mock_execute.return_value = {
            "available_catalogs": ["dev", "prod"],
            "current_catalog": "dev",
            "user_info": {"email": "test@example.com"},
            "total_count": 2
        }
        
        with patch('builtins.print') as mock_print:
            _handle_list_command("https://test.com", False)
            
            # Check that success message was printed
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            self.assertTrue(any("Available Catalogs" in call for call in print_calls))
            self.assertTrue(any("dev (current)" in call for call in print_calls))
            self.assertTrue(any("Total: 2 catalogs" in call for call in print_calls))

    @patch("zededa_edgeai_sdk.commands.catalogs.execute_catalog_list")
    def test_handle_list_command_empty_list(self, mock_execute):
        """Test CLI handler for empty catalog list."""
        mock_execute.return_value = {
            "available_catalogs": [],
            "current_catalog": None,
            "user_info": {"email": "test@example.com"},
            "total_count": 0
        }
        
        with patch('builtins.print') as mock_print:
            _handle_list_command("https://test.com", False)
            
            # Check that empty message was printed
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            self.assertTrue(any("No catalogs available" in call for call in print_calls))

    @patch.dict(os.environ, {}, clear=True)
    def test_handle_cli_list_option(self):
        """Test CLI handler with --list option."""
        args = argparse.Namespace(
            list=True,
            switch=None,
            service_url=None,
            debug=False
        )
        
        with patch('zededa_edgeai_sdk.commands.catalogs._handle_list_command') as mock_handle:
            handle_cli(args)
            # The service_url gets resolved to default, not None
            mock_handle.assert_called_once_with("https://studio.edgeai.zededa.dev", False)

    def test_handle_cli_no_options(self):
        """Test CLI handler with no --list option."""
        args = argparse.Namespace(
            list=False,
            service_url=None,
            debug=False
        )
        
        with patch('builtins.print') as mock_print:
            with self.assertRaises(SystemExit) as context:
                handle_cli(args)
            
            self.assertEqual(context.exception.code, 1)
            # Check that both error messages are printed
            mock_print.assert_any_call("Error: --list parameter is required")
            mock_print.assert_any_call("Use 'zededa-edgeai set-catalog-context <catalog>' to switch catalogs")

    def test_register_command_with_list_option(self):
        """Test command registration includes --list option."""
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()
        
        # Register the command
        CATALOGS_COMMAND.register(subparsers)
        
        # Test parsing --list argument
        catalog_parser = subparsers._name_parser_map["catalog"]
        
        args = catalog_parser.parse_args(["--list"])
        self.assertTrue(args.list)
        self.assertIsNone(args.service_url)
        self.assertFalse(args.debug)
        
        # Test parsing both options together (should work)
        args = catalog_parser.parse_args(["--list", "--debug"])
        self.assertTrue(args.list)
        self.assertTrue(args.debug)


if __name__ == "__main__":
    unittest.main()