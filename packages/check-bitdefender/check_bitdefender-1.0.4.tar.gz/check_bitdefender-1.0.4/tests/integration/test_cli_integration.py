"""Integration tests for CLI interface end-to-end without external dependencies."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from check_bitdefender.cli import main


@pytest.fixture
def cli_runner():
    """Create CLI runner for testing."""
    return CliRunner()


class TestHelpCommand:
    """Test help command functionality."""

    def test_help_command(self, cli_runner):
        """Test help command displays usage information."""
        result = cli_runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert (
            "Check BitDefender GravityZone API endpoints and validate values."
            in result.output
        )
        assert "Commands:" in result.output
        assert "endpoints" in result.output
        assert "lastseen" in result.output
        assert "onboarding" in result.output

    def test_help_flag(self, cli_runner):
        """Test --help flag displays usage information."""
        result = cli_runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert (
            "Check BitDefender GravityZone API endpoints and validate values."
            in result.output
        )


class TestLastSeenCommand:
    """Test lastseen command functionality."""

    @patch("check_bitdefender.cli.commands.lastseen.load_config")
    def test_lastseen_command_error(self, mock_config, cli_runner):
        """Test lastseen command error handling."""
        mock_config.side_effect = Exception("Configuration error")

        result = cli_runner.invoke(main, ["lastseen", "-d", "endpoint.domain.tld"])

        # Exit code should be 3 for UNKNOWN error
        assert result.exit_code == 3
        assert "UNKNOWN: Configuration error" in result.output

    def test_lastseen_command_help(self, cli_runner):
        """Test lastseen command help displays usage information."""
        result = cli_runner.invoke(main, ["lastseen", "--help"])

        assert result.exit_code == 0
        assert "Check endpoint last seen status" in result.output


class TestOnboardingCommand:
    """Test onboarding command functionality."""

    @patch("check_bitdefender.cli.commands.onboarding.load_config")
    def test_onboarding_command_error(self, mock_config, cli_runner):
        """Test onboarding command error handling."""
        mock_config.side_effect = Exception("Authentication failed")

        result = cli_runner.invoke(main, ["onboarding", "-d", "endpoint.domain.tld"])

        assert result.exit_code == 3
        assert "UNKNOWN: Authentication failed" in result.output

    def test_onboarding_command_help(self, cli_runner):
        """Test onboarding command help displays usage information."""
        result = cli_runner.invoke(main, ["onboarding", "--help"])

        assert result.exit_code == 0
        assert "Check endpoint onboarding status" in result.output



class TestEndpointsCommand:
    """Test endpoints command functionality."""

    @patch("check_bitdefender.cli.commands.endpoints.load_config")
    def test_endpoints_command_error(self, mock_config, cli_runner):
        """Test endpoints command error handling."""
        mock_config.side_effect = Exception("Configuration error")

        result = cli_runner.invoke(main, ["endpoints"])

        # Exit code should be 3 for UNKNOWN error
        assert result.exit_code == 3
        assert "UNKNOWN: Configuration error" in result.output
