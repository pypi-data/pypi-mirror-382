"""Test module for bisslog_schema CLI using pytest."""

import pytest
from unittest.mock import patch, MagicMock
import argparse
import sys
from bisslog_schema.cli import main

class TestCLICommandParsing:
    """Test suite for CLI command parsing functionality."""

    @pytest.fixture
    def mock_args(self):
        """Fixture providing default mock arguments for analyze_metadata."""
        args = MagicMock()
        args.command = "analyze_metadata"
        args.path = "/test/path.yaml"
        args.format_file = "yaml"
        args.encoding = "utf-8"
        args.min_warnings = None
        return args

    @patch('bisslog_schema.cli.analyze_command')
    @patch('bisslog_schema.cli.argparse.ArgumentParser.parse_args')
    def test_analyze_metadata_full_args(self, mock_parse, mock_analyze, mock_args):
        """Test command with all arguments specified."""
        mock_args.min_warnings = 0.7
        mock_args.format_file = "json"
        mock_parse.return_value = mock_args

        main()
        mock_analyze.assert_called_once_with(
            "/test/path.yaml",
            format_file="json",
            encoding="utf-8",
            min_warnings=0.7
        )

class TestCLIErrorHandling:
    """Test suite for CLI error handling scenarios."""

    @patch('bisslog_schema.cli.sys.exit')
    @patch('bisslog_schema.cli.argparse.ArgumentParser.parse_args')
    def test_analyze_command_failure(self, mock_parse, mock_exit):
        """Test error handling when analyze_command fails."""
        args = MagicMock()
        args.command = "analyze_metadata"
        mock_parse.return_value = args

        test_error = ValueError("Test error")
        with patch('bisslog_schema.cli.analyze_command', side_effect=test_error), \
             patch('builtins.print') as mock_print:
            main()
            mock_print.assert_called_once_with(f"Error: {str(test_error)}", file=sys.stderr)
            mock_exit.assert_called_once_with(2)

class TestArgumentValidation:
    """Test suite for argument validation."""

    @patch('bisslog_schema.cli.argparse.ArgumentParser.parse_args')
    def test_format_file_validation(self, mock_parse):
        """Test format_file validation."""
        # Test invalid format
        args = MagicMock()
        args.command = "analyze_metadata"
        args.path = "/test/path.yaml"
        args.format_file = "invalid"
        args.encoding = "utf-8"
        args.min_warnings = None
        mock_parse.return_value = args

        # The actual validation happens in the add_argument, so we need to test the error handling
        with patch('bisslog_schema.cli.analyze_command', side_effect=ValueError("Invalid format")):
            with patch('builtins.print') as mock_print:
                with patch("sys.exit") as mock_exit:
                    main()
                    mock_print.assert_called_once_with("Error: Invalid format", file=sys.stderr)
                    mock_exit.assert_called_once_with(2)
