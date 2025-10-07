"""Test cases for the set-catalog-context command functionality."""

import argparse
import os
import unittest
from unittest.mock import MagicMock, patch

from zededa_edgeai_sdk.commands.set_catalog_context import (
    handle_set_catalog_context,
    SET_CATALOG_CONTEXT_COMMAND,
)
from zededa_edgeai_sdk.exceptions import AuthenticationError


class TestSetCatalogContextCommand(unittest.TestCase):
    """Test the set-catalog-context command functionality."""

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

    @patch('zededa_edgeai_sdk.commands.set_catalog_context._launch_shell')
    @patch('zededa_edgeai_sdk.commands.set_catalog_context.execute_catalog_switch')
    def test_handle_set_catalog_context_success(self, mock_execute_switch, mock_launch_shell):
        """Test successful set-catalog-context command handling."""
        # Mock execute_catalog_switch response
        mock_execute_switch.return_value = {
            "catalog_id": "production",
            "environment": {
                "EDGEAI_CURRENT_CATALOG": "production",
                "AWS_ACCESS_KEY_ID": "test_key"
            }
        }
        
        # Set up environment variables for shell launch
        os.environ["EDGEAI_CURRENT_CATALOG"] = "production"
        os.environ["AWS_ACCESS_KEY_ID"] = "test_key"
        
        args = argparse.Namespace(
            catalog="production",
            service_url="https://test.com",
            debug=False
        )
        
        with patch('builtins.print') as mock_print:
            handle_set_catalog_context(args)
            
            # Verify catalog switch was called
            mock_execute_switch.assert_called_once_with(
                "production",
                service_url="https://test.com",
                debug=False
            )
            
            # Verify shell was launched
            mock_launch_shell.assert_called_once()
            
            # Verify success message was printed
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            self.assertTrue(any("Successfully switched to catalog: production" in call for call in print_calls))
            self.assertTrue(any("Launching interactive shell..." in call for call in print_calls))

    @patch('zededa_edgeai_sdk.commands.set_catalog_context.execute_catalog_switch')
    def test_handle_set_catalog_context_auth_error(self, mock_execute_switch):
        """Test set-catalog-context with authentication error."""
        mock_execute_switch.side_effect = AuthenticationError("Not logged in")
        
        args = argparse.Namespace(
            catalog="dev",
            service_url=None,
            debug=False
        )
        
        with patch('builtins.print') as mock_print:
            with self.assertRaises(SystemExit) as context:
                handle_set_catalog_context(args)
            
            self.assertEqual(context.exception.code, 1)
            mock_print.assert_called_with("Catalog context switch failed: Not logged in")

    @patch('zededa_edgeai_sdk.commands.set_catalog_context.execute_catalog_switch')
    def test_handle_set_catalog_context_value_error(self, mock_execute_switch):
        """Test set-catalog-context with value error."""
        mock_execute_switch.side_effect = ValueError("Invalid catalog ID")
        
        args = argparse.Namespace(
            catalog="invalid",
            service_url=None,
            debug=False
        )
        
        with patch('builtins.print') as mock_print:
            with self.assertRaises(SystemExit) as context:
                handle_set_catalog_context(args)
            
            self.assertEqual(context.exception.code, 1)
            mock_print.assert_called_with("Error: Invalid catalog ID")

    @patch('zededa_edgeai_sdk.commands.set_catalog_context.execute_catalog_switch')
    def test_handle_set_catalog_context_keyboard_interrupt(self, mock_execute_switch):
        """Test set-catalog-context with keyboard interrupt."""
        mock_execute_switch.side_effect = KeyboardInterrupt()
        
        args = argparse.Namespace(
            catalog="dev",
            service_url=None,
            debug=False
        )
        
        with patch('builtins.print') as mock_print:
            with self.assertRaises(SystemExit) as context:
                handle_set_catalog_context(args)
            
            self.assertEqual(context.exception.code, 1)
            mock_print.assert_called_with("\nCatalog context switch cancelled by user.")

    def test_command_spec_attributes(self):
        """Test that the command spec has correct attributes."""
        self.assertEqual(SET_CATALOG_CONTEXT_COMMAND.name, "set-catalog-context")
        self.assertEqual(SET_CATALOG_CONTEXT_COMMAND.help, "Switch to catalog and launch authenticated shell")
        self.assertIsNotNone(SET_CATALOG_CONTEXT_COMMAND.register)

    def test_register_creates_parser_with_options(self):
        """Test that the register function creates parser with correct options."""
        import argparse
        
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()
        
        # Register the set-catalog-context command
        SET_CATALOG_CONTEXT_COMMAND.register(subparsers)
        
        # Test parsing catalog argument
        args = parser.parse_args(["set-catalog-context", "production"])
        self.assertEqual(args.catalog, "production")
        self.assertIsNone(args.service_url)
        self.assertFalse(args.debug)
        
        # Test with all options
        args = parser.parse_args([
            "set-catalog-context", "dev",
            "--service-url", "https://custom.backend.com",
            "--debug"
        ])
        self.assertEqual(args.catalog, "dev")
        self.assertEqual(args.service_url, "https://custom.backend.com")
        self.assertTrue(args.debug)


if __name__ == "__main__":
    unittest.main()