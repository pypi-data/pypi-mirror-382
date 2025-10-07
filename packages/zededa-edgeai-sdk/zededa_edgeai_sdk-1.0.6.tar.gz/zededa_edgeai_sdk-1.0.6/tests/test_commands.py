"""Test cases for the command registry and login command functionality."""

import argparse
import os
import unittest
from unittest.mock import MagicMock, patch

from zededa_edgeai_sdk.commands import (
    CommandSpec,
    get_command,
    iter_commands,
    register_subcommands,
)
from zededa_edgeai_sdk.commands.login import (
    execute_login,
    _normalize_catalog,
    _mask,
)
from zededa_edgeai_sdk.exceptions import AuthenticationError


class TestCommandRegistry(unittest.TestCase):
    """Test the command registration and discovery system."""

    def test_command_spec_creation(self):
        """Test CommandSpec dataclass functionality."""
        def dummy_register(subparsers):
            pass
        
        cmd = CommandSpec(
            name="test",
            help="Test command",
            register=dummy_register
        )
        
        self.assertEqual(cmd.name, "test")
        self.assertEqual(cmd.help, "Test command")
        self.assertEqual(cmd.register, dummy_register)

    def test_iter_commands_returns_all_commands(self):
        """Test that iter_commands yields all available commands (login, catalog, logout, set-catalog-context)."""
        commands = list(iter_commands())
        self.assertEqual(len(commands), 4)
        command_names = [cmd.name for cmd in commands]
        self.assertIn("login", command_names)
        self.assertIn("catalog", command_names)
        self.assertIn("logout", command_names)

    def test_get_command_finds_login(self):
        """Test get_command can find the login command."""
        cmd = get_command("login")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.name, "login")

    def test_get_command_returns_none_for_nonexistent(self):
        """Test get_command returns None for non-existent commands."""
        cmd = get_command("nonexistent")
        self.assertIsNone(cmd)

    def test_register_subcommands(self):
        """Test that register_subcommands calls command register functions."""
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()
        
        # Should not raise an exception
        register_subcommands(subparsers)
        
        # Verify login subcommand was added by checking choices
        self.assertIn("login", subparsers._name_parser_map)
        # This would raise SystemExit due to --help, but we're testing the setup


class TestLoginCommand(unittest.TestCase):
    """Test the login command functionality."""

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

    def test_normalize_catalog_with_valid_string(self):
        """Test catalog normalization with valid string."""
        result = _normalize_catalog("  development  ")
        self.assertEqual(result, "development")

    def test_normalize_catalog_with_empty_string(self):
        """Test catalog normalization with empty string."""
        result = _normalize_catalog("")
        self.assertIsNone(result)
        
        result = _normalize_catalog("   ")
        self.assertIsNone(result)

    def test_normalize_catalog_with_none(self):
        """Test catalog normalization with None."""
        result = _normalize_catalog(None)
        self.assertIsNone(result)

    def test_mask_with_long_string(self):
        """Test string masking with long values."""
        result = _mask("very_long_secret_token_12345")
        self.assertEqual(result, "very...45")

    def test_mask_with_short_string(self):
        """Test string masking with short values."""
        result = _mask("short")
        self.assertEqual(result, "shor...rt")

    def test_mask_with_none(self):
        """Test string masking with None."""
        result = _mask(None)
        self.assertIsNone(result)

    def test_mask_with_empty_string(self):
        """Test string masking with empty string."""
        result = _mask("")
        self.assertEqual(result, "")

    @patch("zededa_edgeai_sdk.commands.login._login_with_browser")
    @patch("zededa_edgeai_sdk.commands.login.apply_environment")
    @patch("zededa_edgeai_sdk.commands.login.sanitize_credentials")
    def test_execute_login_browser_flow(self, mock_sanitize, mock_apply_env, mock_browser_login):
        """Test execute_login with browser flow."""
        # Mock return values
        mock_browser_login.return_value = {
            "backend_jwt": "token123",
            "catalog_id": "dev"
        }
        mock_apply_env.return_value = {"MLFLOW_TRACKING_TOKEN": "token123"}
        mock_sanitize.return_value = {"backend_jwt": "***", "catalog_id": "dev"}
        
        result = execute_login("dev", service_url="https://test.com")
        
        # Verify browser login was called
        mock_browser_login.assert_called_once()
        mock_apply_env.assert_called_once()
        mock_sanitize.assert_called_once()
        
        self.assertEqual(result["catalog_id"], "dev")

    @patch("zededa_edgeai_sdk.commands.login._login_with_credentials")
    @patch("zededa_edgeai_sdk.commands.login.apply_environment")
    @patch("zededa_edgeai_sdk.commands.login.sanitize_credentials")
    def test_execute_login_credentials_flow(self, mock_sanitize, mock_apply_env, mock_cred_login):
        """Test execute_login with email/password credentials."""
        # Mock return values
        mock_cred_login.return_value = {
            "backend_jwt": "token123",
            "catalog_id": "dev"
        }
        mock_apply_env.return_value = {"MLFLOW_TRACKING_TOKEN": "token123"}
        mock_sanitize.return_value = {"backend_jwt": "***", "catalog_id": "dev"}
        
        result = execute_login(
            "dev",
            email="user@test.com",
            password="password123",
            service_url="https://test.com"
        )
        
        # Verify credentials login was called
        mock_cred_login.assert_called_once()
        mock_apply_env.assert_called_once()
        mock_sanitize.assert_called_once()
        
        self.assertEqual(result["catalog_id"], "dev")

    def test_execute_login_missing_password_error(self):
        """Test execute_login raises error when email provided without password."""
        with self.assertRaises(ValueError) as context:
            execute_login("dev", email="user@test.com")
        
        self.assertIn("Password is required", str(context.exception))

    def test_execute_login_missing_email_error(self):
        """Test execute_login raises error when password provided without email."""
        with self.assertRaises(ValueError) as context:
            execute_login("dev", password="password123")
        
        self.assertIn("Email is required", str(context.exception))

    @patch("zededa_edgeai_sdk.commands.login.getpass")
    @patch("zededa_edgeai_sdk.commands.login._login_with_credentials")
    @patch("zededa_edgeai_sdk.commands.login.apply_environment")
    @patch("zededa_edgeai_sdk.commands.login.sanitize_credentials")
    def test_execute_login_prompt_password(self, mock_sanitize, mock_apply_env, 
                                         mock_cred_login, mock_getpass):
        """Test execute_login with password prompting."""
        mock_getpass.return_value = "prompted_password"
        mock_cred_login.return_value = {"backend_jwt": "token123", "catalog_id": "dev"}
        mock_apply_env.return_value = {"MLFLOW_TRACKING_TOKEN": "token123"}
        mock_sanitize.return_value = {"backend_jwt": "***", "catalog_id": "dev"}
        
        result = execute_login(
            "dev",
            email="user@test.com",
            prompt_password=True,
            service_url="https://test.com"
        )
        
        # Verify password was prompted
        mock_getpass.assert_called_once_with("Password: ")
        mock_cred_login.assert_called_once()
        
        # Check that prompted password was used in credentials login call
        call_args = mock_cred_login.call_args
        self.assertEqual(call_args[0][4], "prompted_password")  # password argument


if __name__ == "__main__":
    unittest.main()