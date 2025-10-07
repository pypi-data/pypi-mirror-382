"""Test cases for CLI interface and main entry points."""

import sys
import unittest
from io import StringIO
from unittest.mock import patch, Mock

from zededa_edgeai_sdk import cli
from zededa_edgeai_sdk.cli import main
from zededa_edgeai_sdk.exceptions import UserCancelledError, AuthenticationError


class TestCLI(unittest.TestCase):
    """Test CLI interface and argument parsing."""

    def setUp(self):
        """Set up test environment."""
        self.original_argv = sys.argv[:]

    def tearDown(self):
        """Restore original argv."""
        sys.argv = self.original_argv

    @patch('zededa_edgeai_sdk.commands.register_subcommands')
    def test_main_with_no_args_shows_help(self, mock_register):
        """Test that main with no arguments shows help."""
        # Mock register function to avoid actual command registration
        mock_register.return_value = None
        
        # Capture stdout
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            sys.argv = ['edgeai-sdk']
            with self.assertRaises(SystemExit) as cm:
                main()
        
        output = mock_stdout.getvalue()
        self.assertIn("usage:", output.lower())
        self.assertEqual(cm.exception.code, 1)

    @patch('zededa_edgeai_sdk.commands.register_subcommands')
    def test_main_with_help_flag(self, mock_register):
        """Test that main with -h shows help."""
        mock_register.return_value = None
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            sys.argv = ['edgeai-sdk', '-h']
            with self.assertRaises(SystemExit) as cm:
                main()
        
        output = mock_stdout.getvalue()
        self.assertIn("usage:", output.lower())
        self.assertEqual(cm.exception.code, 0)

    @patch('zededa_edgeai_sdk.commands.register_subcommands')
    def test_main_with_unknown_command(self, mock_register):
        """Test that main with unknown command shows error."""
        mock_register.return_value = None
        
        with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
            sys.argv = ['edgeai-sdk', 'unknown-command']
            with self.assertRaises(SystemExit) as cm:
                main()
        
        output = mock_stderr.getvalue()
        self.assertIn("invalid choice", output.lower())
        self.assertEqual(cm.exception.code, 2)

    def test_cli_module_has_main_function(self):
        """Test that CLI module exposes main function."""
        self.assertTrue(hasattr(cli, 'main'))
        self.assertTrue(callable(cli.main))

    def test_cli_main_function_signature(self):
        """Test CLI main function accepts no required arguments."""
        # Should be able to call main() without arguments
        import inspect
        sig = inspect.signature(cli.main)
        required_params = [p for p in sig.parameters.values() 
                          if p.default is inspect.Parameter.empty]
        self.assertEqual(len(required_params), 0)


if __name__ == "__main__":
    unittest.main()